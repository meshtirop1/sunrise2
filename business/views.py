from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.models import ContactSubmission

from .models import Client, Invoice, Project, Proposal
from .services import send_invoice_email, send_proposal_email


@staff_member_required
def dashboard(request):
    """Staff overview: proposals, invoices, projects and enquiries at a glance."""
    proposals = Proposal.objects.select_related('client')
    invoices = Invoice.objects.select_related('client').prefetch_related('items', 'payments')
    projects = Project.objects.select_related('client')
    enquiries = ContactSubmission.objects.all()

    open_invoices = [i for i in invoices if i.status in (Invoice.STATUS_SENT, Invoice.STATUS_PARTIAL)]
    outstanding = sum((i.balance for i in open_invoices), 0)
    overdue = [i for i in open_invoices if i.is_overdue]

    context = {
        'stats': {
            'draft_proposals': proposals.filter(status=Proposal.STATUS_DRAFT).count(),
            'sent_proposals': proposals.filter(status=Proposal.STATUS_SENT).count(),
            'accepted_proposals': proposals.filter(status=Proposal.STATUS_ACCEPTED).count(),
            'outstanding': outstanding,
            'overdue_count': len(overdue),
            'active_projects': projects.filter(status=Project.STATUS_IN_PROGRESS).count(),
            'new_enquiries': enquiries.filter(is_processed=False).count(),
            'clients': Client.objects.count(),
        },
        'recent_proposals': proposals[:8],
        'open_invoices': sorted(open_invoices, key=lambda i: (not i.is_overdue, i.due_date or i.created_at.date()))[:8],
        'active_projects': projects.exclude(status=Project.STATUS_COMPLETED)[:8],
        'recent_enquiries': enquiries.filter(is_processed=False)[:8],
    }
    return render(request, 'business/dashboard.html', context)


@staff_member_required
@require_POST
def dashboard_send_proposal(request, pk):
    proposal = get_object_or_404(Proposal, pk=pk)
    ok, msg = send_proposal_email(proposal, request_user=request.user)
    messages.success(request, msg) if ok else messages.error(request, msg)
    return redirect('business:dashboard')


@staff_member_required
@require_POST
def dashboard_send_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    ok, msg = send_invoice_email(invoice)
    messages.success(request, msg) if ok else messages.error(request, msg)
    return redirect('business:dashboard')
