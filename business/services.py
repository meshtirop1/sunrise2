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
