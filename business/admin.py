from django.contrib import admin, messages
from django.http import HttpResponse
from django.urls import path, reverse
from django.utils.html import format_html

from .models import (Client, EmailLog, Invoice, InvoiceItem, Payment,
                     Project, ProjectNote, Proposal, ProposalItem)
from .services import (render_invoice_pdf, render_proposal_pdf, render_receipt_pdf,
                       send_invoice_email, send_proposal_email, send_receipt_email)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'phone', 'created_at')
    search_fields = ('name', 'company', 'email', 'phone')


class ProposalItemInline(admin.TabularInline):
    model = ProposalItem
    extra = 1
    fields = ('description', 'quantity', 'unit', 'unit_price', 'order')


class EmailLogInline(admin.TabularInline):
    model = EmailLog
    extra = 0
    can_delete = False
    readonly_fields = ('to_email', 'subject', 'sent_at', 'success', 'error')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('reference', 'kind', 'title', 'client', 'status', 'total_display',
                    'sent_at', 'pdf_link')
    list_filter = ('kind', 'status')
    search_fields = ('reference', 'title', 'client__name', 'client__company')
    readonly_fields = ('reference', 'status', 'sent_at', 'sent_to', 'created_at', 'updated_at')
    inlines = [ProposalItemInline, EmailLogInline]
    actions = ['send_to_client']
    fieldsets = (
        (None, {'fields': ('kind', 'reference', 'client', 'title')}),
        ('Content', {'fields': ('introduction', 'scope_of_work', 'terms',
                                'validity_days', 'show_prices')}),
        ('Status', {'fields': ('status', 'sent_at', 'sent_to', 'created_at', 'updated_at')}),
    )

    @admin.display(description='Total (KES)')
    def total_display(self, obj):
        return f"{obj.total:,.2f}"

    @admin.display(description='PDF')
    def pdf_link(self, obj):
        url = reverse('admin:business_proposal_pdf', args=[obj.pk])
        return format_html('<a href="{}">Download</a>', url)

    def get_urls(self):
        urls = super().get_urls()
        extra = [
            path('<int:pk>/pdf/', self.admin_site.admin_view(self.pdf_view),
                 name='business_proposal_pdf'),
        ]
        return extra + urls

    def pdf_view(self, request, pk):
        proposal = self.get_object(request, pk)
        pdf = render_proposal_pdf(proposal)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{proposal.reference}.pdf"'
        return response

    @admin.action(description='Send selected proposals to client by email')
    def send_to_client(self, request, queryset):
        for proposal in queryset:
            ok, msg = send_proposal_email(proposal, request_user=request.user)
            self.message_user(request, msg,
                              level=messages.SUCCESS if ok else messages.ERROR)

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'to_email', 'subject', 'sent_at', 'success')
    list_filter = ('success',)
    search_fields = ('to_email', 'subject', 'proposal__reference')
    readonly_fields = ('proposal', 'to_email', 'subject', 'sent_at', 'success', 'error')

    def has_add_permission(self, request):
        return False


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ('description', 'quantity', 'unit', 'unit_price', 'order')


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('receipt_number', 'amount', 'method', 'transaction_ref',
              'received_on', 'receipt_sent_at')
    readonly_fields = ('receipt_number', 'receipt_sent_at')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('reference', 'title', 'client', 'status', 'total_display',
                    'paid_display', 'balance_display', 'due_date', 'overdue_flag', 'pdf_link')
    list_filter = ('status',)
    search_fields = ('reference', 'title', 'client__name', 'client__company')
    readonly_fields = ('reference', 'status', 'sent_at', 'sent_to', 'created_at', 'updated_at')
    autocomplete_fields = ('client', 'proposal')
    inlines = [InvoiceItemInline, PaymentInline]
    actions = ['send_to_client']
    fieldsets = (
        (None, {'fields': ('reference', 'client', 'proposal', 'title', 'due_date', 'notes')}),
        ('Status', {'fields': ('status', 'sent_at', 'sent_to', 'created_at', 'updated_at')}),
    )

    @admin.display(description='Total (KES)')
    def total_display(self, obj):
        return f"{obj.total:,.2f}"

    @admin.display(description='Paid (KES)')
    def paid_display(self, obj):
        return f"{obj.amount_paid:,.2f}"

    @admin.display(description='Balance (KES)')
    def balance_display(self, obj):
        return f"{obj.balance:,.2f}"

    @admin.display(description='Overdue', boolean=True)
    def overdue_flag(self, obj):
        return obj.is_overdue

    @admin.display(description='PDF')
    def pdf_link(self, obj):
        url = reverse('admin:business_invoice_pdf', args=[obj.pk])
        return format_html('<a href="{}">Download</a>', url)

    def get_urls(self):
        urls = super().get_urls()
        extra = [
            path('<int:pk>/pdf/', self.admin_site.admin_view(self.pdf_view),
                 name='business_invoice_pdf'),
        ]
        return extra + urls

    def pdf_view(self, request, pk):
        invoice = self.get_object(request, pk)
        response = HttpResponse(render_invoice_pdf(invoice), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{invoice.reference}.pdf"'
        return response

    @admin.action(description='Send selected invoices to client by email')
    def send_to_client(self, request, queryset):
        for invoice in queryset:
            ok, msg = send_invoice_email(invoice)
            self.message_user(request, msg,
                              level=messages.SUCCESS if ok else messages.ERROR)

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.refresh_payment_status()


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'invoice', 'amount', 'method',
                    'received_on', 'receipt_sent_at', 'receipt_link')
    list_filter = ('method',)
    search_fields = ('receipt_number', 'transaction_ref', 'invoice__reference',
                     'invoice__client__name')
    readonly_fields = ('receipt_number', 'receipt_sent_at', 'recorded_at')
    autocomplete_fields = ('invoice',)
    actions = ['send_receipt']

    @admin.display(description='Receipt PDF')
    def receipt_link(self, obj):
        url = reverse('admin:business_payment_pdf', args=[obj.pk])
        return format_html('<a href="{}">Download</a>', url)

    def get_urls(self):
        urls = super().get_urls()
        extra = [
            path('<int:pk>/pdf/', self.admin_site.admin_view(self.pdf_view),
                 name='business_payment_pdf'),
        ]
        return extra + urls

    def pdf_view(self, request, pk):
        payment = self.get_object(request, pk)
        response = HttpResponse(render_receipt_pdf(payment), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{payment.receipt_number}.pdf"'
        return response

    @admin.action(description='Email receipt to client')
    def send_receipt(self, request, queryset):
        for payment in queryset:
            ok, msg = send_receipt_email(payment)
            self.message_user(request, msg,
                              level=messages.SUCCESS if ok else messages.ERROR)


class ProjectNoteInline(admin.TabularInline):
    model = ProjectNote
    extra = 1
    fields = ('date', 'note', 'author')
    readonly_fields = ('author',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'status', 'site_location', 'crew_lead',
                    'start_date', 'target_end_date', 'completed_on')
    list_filter = ('status',)
    search_fields = ('name', 'client__name', 'site_location', 'crew_lead')
    autocomplete_fields = ('client', 'proposal')
    inlines = [ProjectNoteInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, ProjectNote) and not obj.author_id:
                obj.author = request.user
            obj.save()
        for obj in formset.deleted_objects:
            obj.delete()
        formset.save_m2m()
