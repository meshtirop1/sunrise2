from django.conf import settings
from django.db import models
from django.utils import timezone


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
