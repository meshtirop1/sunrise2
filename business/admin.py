from django.contrib import admin, messages
from django.http import HttpResponse
from django.urls import path, reverse
from django.utils.html import format_html

from .models import Client, EmailLog, Proposal, ProposalItem
from .services import render_proposal_pdf, send_proposal_email


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
