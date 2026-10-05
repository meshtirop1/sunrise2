"""PDF rendering and email delivery for proposals and quotations."""
import io
import os

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone

from xhtml2pdf import pisa

from .models import EmailLog


def _link_callback(uri, rel):
    """Resolve static/media URIs to filesystem paths for xhtml2pdf."""
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.BASE_DIR, 'static', uri[len(settings.STATIC_URL):].lstrip('/'))
    elif uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri[len(settings.MEDIA_URL):].lstrip('/'))
    else:
        return uri
    return path


def render_proposal_pdf(proposal):
    """Render a proposal to PDF bytes using the branded template."""
    html = render_to_string('business/proposal_pdf.html', {
        'proposal': proposal,
        'company': settings.COMPANY_INFO,
        'today': timezone.localdate(),
    })
    buffer = io.BytesIO()
    result = pisa.CreatePDF(html, dest=buffer, link_callback=_link_callback)
    if result.err:
        raise RuntimeError(f"PDF generation failed for {proposal.reference}")
    return buffer.getvalue()


def send_proposal_email(proposal, request_user=None):
    """Email the proposal PDF to the client and log the outcome.

    Returns (success, message).
    """
    company = settings.COMPANY_INFO
    kind_label = proposal.get_kind_display()
    subject = f"{kind_label} {proposal.reference}: {proposal.title} – {company['name']}"
    body = (
        f"Dear {proposal.client.name},\n\n"
        f"Please find attached our {kind_label.lower()} {proposal.reference} "
        f"for \"{proposal.title}\".\n\n"
        f"This offer is valid for {proposal.validity_days} days. "
        f"If you have any questions, reply to this email or call us on "
        f"{company['phones'][0]}.\n\n"
        f"Kind regards,\n"
        f"{company['name']}\n"
        f"{company['address']}\n"
        f"{' / '.join(company['phones'])}\n"
        f"{company['website']}"
    )
    try:
        pdf_bytes = render_proposal_pdf(proposal)
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[proposal.client.email],
            reply_to=[settings.DEFAULT_FROM_EMAIL],
        )
        email.attach(f"{proposal.reference}.pdf", pdf_bytes, 'application/pdf')
        email.send(fail_silently=False)
    except Exception as exc:  # noqa: BLE001 - we log and surface any failure
        EmailLog.objects.create(
            proposal=proposal, to_email=proposal.client.email,
            subject=subject, success=False, error=str(exc),
        )
        return False, f"Sending failed: {exc}"

    EmailLog.objects.create(
        proposal=proposal, to_email=proposal.client.email,
        subject=subject, success=True,
    )
    proposal.status = proposal.STATUS_SENT
    proposal.sent_at = timezone.now()
    proposal.sent_to = proposal.client.email
    proposal.save(update_fields=['status', 'sent_at', 'sent_to'])
    return True, f"{kind_label} {proposal.reference} emailed to {proposal.client.email}"


def _render_pdf(template, context):
    html = render_to_string(template, context)
    buffer = io.BytesIO()
    result = pisa.CreatePDF(html, dest=buffer, link_callback=_link_callback)
    if result.err:
        raise RuntimeError(f"PDF generation failed for template {template}")
    return buffer.getvalue()


def render_invoice_pdf(invoice):
    return _render_pdf('business/invoice_pdf.html', {
        'invoice': invoice,
        'company': settings.COMPANY_INFO,
        'today': timezone.localdate(),
    })


def render_receipt_pdf(payment):
    return _render_pdf('business/receipt_pdf.html', {
        'payment': payment,
        'invoice': payment.invoice,
        'company': settings.COMPANY_INFO,
        'today': timezone.localdate(),
    })


def _send_pdf_email(*, to_email, subject, body, filename, pdf_bytes):
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
        reply_to=[settings.DEFAULT_FROM_EMAIL],
    )
    email.attach(filename, pdf_bytes, 'application/pdf')
    email.send(fail_silently=False)


def _signature():
    company = settings.COMPANY_INFO
    return (f"Kind regards,\n{company['name']}\n{company['address']}\n"
            f"{' / '.join(company['phones'])}\n{company['website']}")


def send_invoice_email(invoice):
    """Email the invoice PDF to the client. Returns (success, message)."""
    company = settings.COMPANY_INFO
    subject = f"Invoice {invoice.reference}: {invoice.title} – {company['name']}"
    d = invoice.due_date
    if d and hasattr(d, 'strftime'):
        due = f" Payment is due by {d:%d %b %Y}."
    elif d:
        due = f" Payment is due by {d}."
    else:
        due = ""
    body = (
        f"Dear {invoice.client.name},\n\n"
        f"Please find attached invoice {invoice.reference} for \"{invoice.title}\" "
        f"amounting to KES {invoice.total:,.2f}.{due}\n\n"
        f"If you have any questions, reply to this email or call us on "
        f"{company['phones'][0]}.\n\n" + _signature()
    )
    try:
        _send_pdf_email(to_email=invoice.client.email, subject=subject, body=body,
                        filename=f"{invoice.reference}.pdf",
                        pdf_bytes=render_invoice_pdf(invoice))
    except Exception as exc:  # noqa: BLE001
        return False, f"Sending failed: {exc}"

    if invoice.status == invoice.STATUS_DRAFT:
        invoice.status = invoice.STATUS_SENT
    invoice.sent_at = timezone.now()
    invoice.sent_to = invoice.client.email
    invoice.save(update_fields=['status', 'sent_at', 'sent_to'])
    invoice.refresh_payment_status()
    return True, f"Invoice {invoice.reference} emailed to {invoice.client.email}"


def send_receipt_email(payment):
    """Email a payment receipt PDF to the client. Returns (success, message)."""
    company = settings.COMPANY_INFO
    invoice = payment.invoice
    subject = f"Receipt {payment.receipt_number} – {company['name']}"
    balance = invoice.balance
    closing = ("Your invoice is now fully settled. Thank you for your business!"
               if balance <= 0 else
               f"The outstanding balance on invoice {invoice.reference} is KES {balance:,.2f}.")
    body = (
        f"Dear {invoice.client.name},\n\n"
        f"We confirm receipt of KES {payment.amount:,.2f} "
        f"({payment.get_method_display()}) against invoice {invoice.reference}. "
        f"Your receipt is attached.\n\n{closing}\n\n" + _signature()
    )
    try:
        _send_pdf_email(to_email=invoice.client.email, subject=subject, body=body,
                        filename=f"{payment.receipt_number}.pdf",
                        pdf_bytes=render_receipt_pdf(payment))
    except Exception as exc:  # noqa: BLE001
        return False, f"Sending failed: {exc}"

    payment.receipt_sent_at = timezone.now()
    payment.save(update_fields=['receipt_sent_at'])
    return True, f"Receipt {payment.receipt_number} emailed to {invoice.client.email}"
