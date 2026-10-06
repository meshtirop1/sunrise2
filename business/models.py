import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


def proposal_pdf_path(instance, filename):
    return f"documents/proposals/{instance.reference}-{uuid.uuid4().hex[:8]}.pdf"


def invoice_pdf_path(instance, filename):
    return f"documents/invoices/{instance.reference}-{uuid.uuid4().hex[:8]}.pdf"


def receipt_pdf_path(instance, filename):
    return f"documents/receipts/{instance.receipt_number}-{uuid.uuid4().hex[:8]}.pdf"


class Client(models.Model):
    """A customer or prospect we send proposals, quotations and invoices to."""
    name = models.CharField(max_length=200, help_text="Contact person or organisation name")
    company = models.CharField(max_length=200, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.company})" if self.company else self.name


class Proposal(models.Model):
    """A proposal or quotation written in the admin, rendered to a branded PDF
    and emailed to the client."""

    KIND_PROPOSAL = 'proposal'
    KIND_QUOTATION = 'quotation'
    KIND_CHOICES = [
        (KIND_PROPOSAL, 'Proposal'),
        (KIND_QUOTATION, 'Quotation'),
    ]

    STATUS_DRAFT = 'draft'
    STATUS_SENT = 'sent'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SENT, 'Sent'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default=KIND_PROPOSAL)
    reference = models.CharField(max_length=30, unique=True, blank=True,
                                 help_text="Auto-generated if left blank, e.g. SDL-P-2026-001")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='proposals')
    title = models.CharField(max_length=255, help_text="e.g. Borehole Drilling & Equipping – Kapsoya Farm")
    introduction = models.TextField(
        blank=True,
        help_text="Opening paragraph addressed to the client. Plain text; blank lines start new paragraphs.")
    scope_of_work = models.TextField(
        blank=True,
        help_text="What we will do. One item per line to render as a bullet list.")
    terms = models.TextField(
        blank=True,
        default=("Payment: 60% deposit on commencement, 40% on completion.\n"
                 "This offer is valid for 30 days from the date above.\n"
                 "Prices are inclusive of transport within Uasin Gishu County."),
        help_text="Terms and conditions. One item per line.")
    validity_days = models.PositiveIntegerField(default=30)
    show_prices = models.BooleanField(default=True, help_text="Include the pricing table in the PDF")

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='proposals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_to = models.EmailField(blank=True, help_text="Filled automatically when the email is sent")
    pdf_file = models.FileField(upload_to=proposal_pdf_path, blank=True,
                                help_text="Saved copy of the last PDF emailed to the client")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} – {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference:
            prefix = 'SDL-Q' if self.kind == self.KIND_QUOTATION else 'SDL-P'
            year = timezone.now().year
            last = (Proposal.objects
                    .filter(reference__startswith=f"{prefix}-{year}-")
                    .order_by('-reference').values_list('reference', flat=True).first())
            seq = int(last.rsplit('-', 1)[1]) + 1 if last else 1
            self.reference = f"{prefix}-{year}-{seq:03d}"
        super().save(*args, **kwargs)

    @property
    def total(self):
        return sum((item.line_total for item in self.items.all()), 0)

    def scope_lines(self):
        return [l.strip() for l in self.scope_of_work.splitlines() if l.strip()]

    def terms_lines(self):
        return [l.strip() for l in self.terms.splitlines() if l.strip()]

    def intro_paragraphs(self):
        return [p.strip() for p in self.introduction.split('\n\n') if p.strip()]


class ProposalItem(models.Model):
    """A line in the pricing table of a proposal or quotation."""
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(max_length=30, blank=True, help_text="e.g. metres, pcs, lot")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                     help_text="Price in KES")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.description

    @property
    def line_total(self):
        return self.quantity * self.unit_price


class EmailLog(models.Model):
    """Record of every proposal email the system sends."""
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='email_logs')
    to_email = models.EmailField()
    subject = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    error = models.TextField(blank=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        status = 'sent' if self.success else 'FAILED'
        return f"{self.proposal.reference} → {self.to_email} ({status})"


def next_reference(model, prefix, field='reference'):
    """Generate the next sequential reference like SDL-I-2026-003."""
    year = timezone.now().year
    last = (model.objects
            .filter(**{f"{field}__startswith": f"{prefix}-{year}-"})
            .order_by(f"-{field}").values_list(field, flat=True).first())
    seq = int(last.rsplit('-', 1)[1]) + 1 if last else 1
    return f"{prefix}-{year}-{seq:03d}"


class Invoice(models.Model):
    """An invoice written in the admin, rendered to a branded PDF and emailed
    to the client. Payments recorded against it produce receipts."""

    STATUS_DRAFT = 'draft'
    STATUS_SENT = 'sent'
    STATUS_PARTIAL = 'partial'
    STATUS_PAID = 'paid'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SENT, 'Sent'),
        (STATUS_PARTIAL, 'Partially paid'),
        (STATUS_PAID, 'Paid'),
    ]

    reference = models.CharField(max_length=30, unique=True, blank=True,
                                 help_text="Auto-generated if left blank, e.g. SDL-I-2026-001")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='invoices')
    proposal = models.ForeignKey(Proposal, null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name='invoices',
                                 help_text="Optional: the proposal/quotation this invoice follows")
    title = models.CharField(max_length=255, help_text="e.g. Borehole Drilling – Kapsoya Farm, Phase 1")
    notes = models.TextField(blank=True, help_text="Shown on the invoice under the pricing table")
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='invoices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_to = models.EmailField(blank=True)
    pdf_file = models.FileField(upload_to=invoice_pdf_path, blank=True,
                                help_text="Saved copy of the last PDF emailed to the client")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} – {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = next_reference(Invoice, 'SDL-I')
        super().save(*args, **kwargs)

    @property
    def total(self):
        return sum((item.line_total for item in self.items.all()), 0)

    @property
    def amount_paid(self):
        return sum((p.amount for p in self.payments.all()), 0)

    @property
    def balance(self):
        return self.total - self.amount_paid

    @property
    def is_overdue(self):
        return (self.due_date and self.balance > 0
                and self.status != self.STATUS_DRAFT
                and timezone.localdate() > self.due_date)

    def refresh_payment_status(self):
        """Update status from recorded payments (draft stays draft until sent)."""
        if self.status == self.STATUS_DRAFT:
            return
        paid = self.amount_paid
        if paid <= 0:
            new = self.STATUS_SENT
        elif paid < self.total:
            new = self.STATUS_PARTIAL
        else:
            new = self.STATUS_PAID
        if new != self.status:
            self.status = new
            self.save(update_fields=['status'])


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(max_length=30, blank=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                     help_text="Price in KES")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.description

    @property
    def line_total(self):
        return self.quantity * self.unit_price


class Payment(models.Model):
    """A payment received against an invoice. Each payment can be emailed to
    the client as a branded receipt."""

    METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank transfer'),
        ('cheque', 'Cheque'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]

    receipt_number = models.CharField(max_length=30, unique=True, blank=True,
                                      help_text="Auto-generated, e.g. SDL-R-2026-001")
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Amount in KES")
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default='mpesa')
    transaction_ref = models.CharField(max_length=100, blank=True,
                                       help_text="e.g. M-Pesa code or bank slip number")
    received_on = models.DateField(default=timezone.localdate)
    recorded_at = models.DateTimeField(auto_now_add=True)
    receipt_sent_at = models.DateTimeField(null=True, blank=True)
    pdf_file = models.FileField(upload_to=receipt_pdf_path, blank=True,
                                help_text="Saved copy of the last receipt PDF emailed to the client")

    class Meta:
        ordering = ['-received_on', '-recorded_at']

    def __str__(self):
        return f"{self.receipt_number} – KES {self.amount} for {self.invoice.reference}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = next_reference(Payment, 'SDL-R', field='receipt_number')
        super().save(*args, **kwargs)
        self.invoice.refresh_payment_status()

    def delete(self, *args, **kwargs):
        invoice = self.invoice
        super().delete(*args, **kwargs)
        invoice.refresh_payment_status()


class Project(models.Model):
    """A job we are executing: links the winning proposal, the client, the
    site and the crew, and carries dated progress notes."""

    STATUS_PLANNED = 'planned'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_ON_HOLD = 'on_hold'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_PLANNED, 'Planned'),
        (STATUS_IN_PROGRESS, 'In progress'),
        (STATUS_ON_HOLD, 'On hold'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    name = models.CharField(max_length=255, help_text="e.g. Kapsoya Farm Borehole")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='projects')
    proposal = models.ForeignKey(Proposal, null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name='projects',
                                 help_text="The accepted proposal this project executes")
    site_location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PLANNED)
    crew_lead = models.CharField(max_length=200, blank=True, help_text="Site supervisor / crew lead")
    start_date = models.DateField(null=True, blank=True)
    target_end_date = models.DateField(null=True, blank=True)
    completed_on = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProjectNote(models.Model):
    """A dated progress note on a project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='notes')
    date = models.DateField(default=timezone.localdate)
    note = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                               on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.project.name} – {self.date}"
