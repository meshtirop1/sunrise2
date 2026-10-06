import calendar
import json
from datetime import date

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import views as auth_views
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST

from main.models import ContactSubmission

from .forms import (ClientForm, InvoiceForm, InvoiceItemFormSet, PaymentForm,
                    ProjectForm, ProjectNoteForm, ProposalForm,
                    ProposalItemFormSet)
from .models import Client, Invoice, Payment, Project, Proposal
from .services import (render_invoice_pdf, render_proposal_pdf,
                       render_receipt_pdf, send_invoice_email,
                       send_proposal_email, send_receipt_email)


def _last_months(n=12):
    """[(year, month), …] for the last n months ending this month."""
    today = timezone.localdate()
    months = []
    year, month = today.year, today.month
    for _ in range(n):
        months.append((year, month))
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    return list(reversed(months))


def _chart_data():
    months = _last_months(12)
    labels = [f"{calendar.month_abbr[m]} {str(y)[2:]}" for y, m in months]
    index = {ym: i for i, ym in enumerate(months)}

    invoiced = [0.0] * len(months)
    for invoice in Invoice.objects.exclude(status=Invoice.STATUS_DRAFT).prefetch_related('items'):
        key = (invoice.created_at.year, invoice.created_at.month)
        if key in index:
            invoiced[index[key]] += float(invoice.total)

    collected = [0.0] * len(months)
    for payment in Payment.objects.all():
        key = (payment.received_on.year, payment.received_on.month)
        if key in index:
            collected[index[key]] += float(payment.amount)

    enquiries = [0] * len(months)
    for submitted in ContactSubmission.objects.values_list('submitted_at', flat=True):
        local = timezone.localtime(submitted)
        key = (local.year, local.month)
        if key in index:
            enquiries[index[key]] += 1

    proposal_counts = {status: 0 for status, _ in Proposal.STATUS_CHOICES}
    for status in Proposal.objects.values_list('status', flat=True):
        proposal_counts[status] = proposal_counts.get(status, 0) + 1

    project_counts = {status: 0 for status, _ in Project.STATUS_CHOICES}
    for status in Project.objects.values_list('status', flat=True):
        project_counts[status] = project_counts.get(status, 0) + 1

    return {
        'labels': labels,
        'invoiced': invoiced,
        'collected': collected,
        'enquiries': enquiries,
        'proposal_status': {
            'labels': [label for _, label in Proposal.STATUS_CHOICES],
            'counts': [proposal_counts[status] for status, _ in Proposal.STATUS_CHOICES],
        },
        'project_status': {
            'labels': [label for _, label in Project.STATUS_CHOICES],
            'counts': [project_counts[status] for status, _ in Project.STATUS_CHOICES],
        },
    }


@staff_member_required(login_url='business:login')
def dashboard(request):
    """Staff overview: KPIs, charts, and work queues at a glance."""
    proposals = Proposal.objects.select_related('client')
    invoices = Invoice.objects.select_related('client').prefetch_related('items', 'payments')
    projects = Project.objects.select_related('client')
    enquiries = ContactSubmission.objects.all()

    open_invoices = [i for i in invoices if i.status in (Invoice.STATUS_SENT, Invoice.STATUS_PARTIAL)]
    outstanding = sum((i.balance for i in open_invoices), 0)
    overdue = [i for i in open_invoices if i.is_overdue]
    year = timezone.localdate().year
    collected_this_year = sum(
        (p.amount for p in Payment.objects.filter(received_on__year=year)), 0)

    context = {
        'stats': {
            'draft_proposals': proposals.filter(status=Proposal.STATUS_DRAFT).count(),
            'sent_proposals': proposals.filter(status=Proposal.STATUS_SENT).count(),
            'accepted_proposals': proposals.filter(status=Proposal.STATUS_ACCEPTED).count(),
            'outstanding': outstanding,
            'overdue_count': len(overdue),
            'collected_this_year': collected_this_year,
            'active_projects': projects.filter(status=Project.STATUS_IN_PROGRESS).count(),
            'new_enquiries': enquiries.filter(is_processed=False).count(),
            'clients': Client.objects.count(),
        },
        'chart_data': json.dumps(_chart_data()),
        'recent_proposals': proposals[:6],
        'open_invoices': sorted(open_invoices,
                                key=lambda i: (not i.is_overdue, i.due_date or i.created_at.date()))[:6],
        'active_projects': projects.exclude(status=Project.STATUS_COMPLETED)[:6],
        'recent_enquiries': enquiries.filter(is_processed=False)[:6],
        'active_tab': 'overview',
    }
    return render(request, 'business/dashboard.html', context)


# ---------------------------------------------------------------- proposals

@staff_member_required(login_url='business:login')
def proposal_list(request):
    qs = Proposal.objects.select_related('client').prefetch_related('items')
    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(reference__icontains=q) | Q(title__icontains=q) |
                       Q(client__name__icontains=q) | Q(client__company__icontains=q))
    return render(request, 'business/proposal_list.html', {
        'proposals': qs[:100], 'status': status, 'q': q,
        'status_choices': Proposal.STATUS_CHOICES, 'active_tab': 'proposals',
    })


@staff_member_required(login_url='business:login')
def proposal_detail(request, pk):
    proposal = get_object_or_404(
        Proposal.objects.select_related('client').prefetch_related('items', 'email_logs'), pk=pk)
    return render(request, 'business/proposal_detail.html', {
        'proposal': proposal, 'active_tab': 'proposals',
    })


def _proposal_form(request, proposal=None):
    if request.method == 'POST':
        form = ProposalForm(request.POST, instance=proposal)
        formset = ProposalItemFormSet(request.POST, instance=proposal)
        if form.is_valid() and formset.is_valid():
            obj = form.save(commit=False)
            if proposal is None:
                obj.created_by = request.user
            obj.save()
            formset.instance = obj
            formset.save()
            messages.success(request, f"{obj.reference} saved.")
            return redirect('business:proposal_detail', pk=obj.pk)
    else:
        form = ProposalForm(instance=proposal)
        formset = ProposalItemFormSet(instance=proposal)
    return render(request, 'business/proposal_form.html', {
        'form': form, 'formset': formset, 'proposal': proposal,
        'active_tab': 'proposals',
    })


@staff_member_required(login_url='business:login')
def proposal_create(request):
    return _proposal_form(request)


@staff_member_required(login_url='business:login')
def proposal_edit(request, pk):
    return _proposal_form(request, get_object_or_404(Proposal, pk=pk))


@staff_member_required(login_url='business:login')
@require_POST
def proposal_set_status(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    status = request.POST.get('status')
    if status in dict(Proposal.STATUS_CHOICES):
        proposal.status = status
        proposal.save(update_fields=['status'])
        messages.success(request, f"{proposal.reference} marked {proposal.get_status_display().lower()}.")
    return redirect('business:proposal_detail', pk=pk)


@staff_member_required(login_url='business:login')
def proposal_pdf(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    response = HttpResponse(render_proposal_pdf(proposal), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{proposal.reference}.pdf"'
    return response


@staff_member_required(login_url='business:login')
@require_POST
def dashboard_send_proposal(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    ok, msg = send_proposal_email(proposal, request_user=request.user)
    messages.success(request, msg) if ok else messages.error(request, msg)
    return redirect(request.POST.get('next') or 'business:dashboard')


# ----------------------------------------------------------------- invoices

@staff_member_required(login_url='business:login')
def invoice_list(request):
    qs = Invoice.objects.select_related('client').prefetch_related('items', 'payments')
    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(reference__icontains=q) | Q(title__icontains=q) |
                       Q(client__name__icontains=q) | Q(client__company__icontains=q))
    return render(request, 'business/invoice_list.html', {
        'invoices': qs[:100], 'status': status, 'q': q,
        'status_choices': Invoice.STATUS_CHOICES, 'active_tab': 'invoices',
    })


@staff_member_required(login_url='business:login')
def invoice_detail(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related('client').prefetch_related('items', 'payments'), pk=pk)
    return render(request, 'business/invoice_detail.html', {
        'invoice': invoice, 'payment_form': PaymentForm(),
        'active_tab': 'invoices',
    })


def _invoice_form(request, invoice=None):
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = InvoiceItemFormSet(request.POST, instance=invoice)
        if form.is_valid() and formset.is_valid():
            obj = form.save(commit=False)
            if invoice is None:
                obj.created_by = request.user
            obj.save()
            formset.instance = obj
            formset.save()
            messages.success(request, f"{obj.reference} saved.")
            return redirect('business:invoice_detail', pk=obj.pk)
    else:
        form = InvoiceForm(instance=invoice)
        formset = InvoiceItemFormSet(instance=invoice)
    return render(request, 'business/invoice_form.html', {
        'form': form, 'formset': formset, 'invoice': invoice,
        'active_tab': 'invoices',
    })


@staff_member_required(login_url='business:login')
def invoice_create(request):
    return _invoice_form(request)


@staff_member_required(login_url='business:login')
def invoice_edit(request, pk):
    return _invoice_form(request, get_object_or_404(Invoice, pk=pk))


@staff_member_required(login_url='business:login')
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    response = HttpResponse(render_invoice_pdf(invoice), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{invoice.reference}.pdf"'
    return response


@staff_member_required(login_url='business:login')
@require_POST
def dashboard_send_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    ok, msg = send_invoice_email(invoice)
    messages.success(request, msg) if ok else messages.error(request, msg)
    return redirect(request.POST.get('next') or 'business:dashboard')


@staff_member_required(login_url='business:login')
@require_POST
def payment_add(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    form = PaymentForm(request.POST)
    if form.is_valid():
        payment = form.save(commit=False)
        payment.invoice = invoice
        payment.save()
        messages.success(request, f"Payment of KES {payment.amount} recorded "
                                  f"(receipt {payment.receipt_number}).")
    else:
        messages.error(request, "Could not record payment — check the amount and date.")
    return redirect('business:invoice_detail', pk=pk)


@staff_member_required(login_url='business:login')
@require_POST
def payment_send_receipt(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    ok, msg = send_receipt_email(payment)
    messages.success(request, msg) if ok else messages.error(request, msg)
    return redirect('business:invoice_detail', pk=payment.invoice_id)


@staff_member_required(login_url='business:login')
def receipt_pdf(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    response = HttpResponse(render_receipt_pdf(payment), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{payment.receipt_number}.pdf"'
    return response


# ----------------------------------------------------------------- projects

@staff_member_required(login_url='business:login')
def project_list(request):
    qs = Project.objects.select_related('client')
    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)
    return render(request, 'business/project_list.html', {
        'projects': qs[:100], 'status': status,
        'status_choices': Project.STATUS_CHOICES, 'active_tab': 'projects',
    })


@staff_member_required(login_url='business:login')
def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related('client').prefetch_related('notes'), pk=pk)
    if request.method == 'POST':
        note_form = ProjectNoteForm(request.POST)
        if note_form.is_valid():
            note = note_form.save(commit=False)
            note.project = project
            note.author = request.user
            note.save()
            messages.success(request, "Progress note added.")
            return redirect('business:project_detail', pk=pk)
    else:
        note_form = ProjectNoteForm()
    return render(request, 'business/project_detail.html', {
        'project': project, 'note_form': note_form, 'active_tab': 'projects',
    })


def _project_form(request, project=None):
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f"Project “{obj.name}” saved.")
            return redirect('business:project_detail', pk=obj.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'business/project_form.html', {
        'form': form, 'project': project, 'active_tab': 'projects',
    })


@staff_member_required(login_url='business:login')
def project_create(request):
    return _project_form(request)


@staff_member_required(login_url='business:login')
def project_edit(request, pk):
    return _project_form(request, get_object_or_404(Project, pk=pk))


@staff_member_required(login_url='business:login')
@require_POST
def project_set_status(request, pk):
    project = get_object_or_404(Project, pk=pk)
    status = request.POST.get('status')
    if status in dict(Project.STATUS_CHOICES):
        project.status = status
        if status == Project.STATUS_COMPLETED and not project.completed_on:
            project.completed_on = date.today()
        project.save()
        messages.success(request, f"“{project.name}” marked {project.get_status_display().lower()}.")
    return redirect('business:project_detail', pk=pk)


# ------------------------------------------------------------------ clients

@staff_member_required(login_url='business:login')
def client_list(request):
    qs = Client.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(company__icontains=q) |
                       Q(email__icontains=q) | Q(phone__icontains=q))
    return render(request, 'business/client_list.html', {
        'clients': qs[:200], 'q': q, 'active_tab': 'clients',
    })


def _client_form(request, client=None):
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f"Client “{obj.name}” saved.")
            return redirect('business:client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'business/client_form.html', {
        'form': form, 'client_obj': client, 'active_tab': 'clients',
    })


@staff_member_required(login_url='business:login')
def client_create(request):
    return _client_form(request)


@staff_member_required(login_url='business:login')
def client_edit(request, pk):
    return _client_form(request, get_object_or_404(Client, pk=pk))


# ---------------------------------------------------------------- enquiries

@staff_member_required(login_url='business:login')
def enquiry_list(request):
    show = request.GET.get('show', 'new')
    qs = ContactSubmission.objects.all()
    if show == 'new':
        qs = qs.filter(is_processed=False)
    return render(request, 'business/enquiry_list.html', {
        'enquiries': qs[:100], 'show': show, 'active_tab': 'enquiries',
    })


@staff_member_required(login_url='business:login')
@require_POST
def enquiry_mark_processed(request, pk):
    enquiry = get_object_or_404(ContactSubmission, pk=pk)
    enquiry.is_processed = True
    enquiry.save(update_fields=['is_processed'])
    messages.success(request, f"Enquiry from {enquiry.name} marked handled.")
    return redirect('business:enquiry_list')


@staff_member_required(login_url='business:login')
@require_POST
def enquiry_to_client(request, pk):
    enquiry = get_object_or_404(ContactSubmission, pk=pk)
    client, created = Client.objects.get_or_create(
        email=enquiry.email,
        defaults={'name': enquiry.name, 'phone': enquiry.phone,
                  'notes': f"Converted from website enquiry ({enquiry.submitted_at:%d %b %Y}):\n"
                           f"{enquiry.message}"})
    enquiry.is_processed = True
    enquiry.save(update_fields=['is_processed'])
    if created:
        messages.success(request, f"“{client.name}” added as a client.")
    else:
        messages.success(request, f"“{client.name}” is already a client — enquiry marked handled.")
    return redirect('business:client_edit', pk=client.pk)


# --------------------------------------------------------------------- auth

class DashboardLoginView(auth_views.LoginView):
    """Branded staff login for /dashboard/."""
    template_name = 'business/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return redirect('business:dashboard')
            messages.error(request,
                           "Your account does not have staff access. "
                           "Ask an administrator to enable it.")
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy('business:dashboard')


class DashboardLogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('main:home')
