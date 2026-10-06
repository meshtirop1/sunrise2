from django import forms
from django.forms import inlineformset_factory

from .models import (Client, Invoice, InvoiceItem, Payment, Project,
                     ProjectNote, Proposal, ProposalItem)


class StyledModelForm(forms.ModelForm):
    """Adds the dashboard input class to every widget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            css = widget.attrs.get('class', '')
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = (css + ' dash-check').strip()
            else:
                widget.attrs['class'] = (css + ' dash-input').strip()


class ClientForm(StyledModelForm):
    class Meta:
        model = Client
        fields = ['name', 'company', 'email', 'phone', 'address', 'notes']
        widgets = {'notes': forms.Textarea(attrs={'rows': 3})}


class ProposalForm(StyledModelForm):
    class Meta:
        model = Proposal
        fields = ['kind', 'client', 'title', 'introduction', 'scope_of_work',
                  'terms', 'validity_days', 'show_prices']
        widgets = {
            'introduction': forms.Textarea(attrs={'rows': 4}),
            'scope_of_work': forms.Textarea(attrs={'rows': 5}),
            'terms': forms.Textarea(attrs={'rows': 4}),
        }


class InvoiceForm(StyledModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'proposal', 'title', 'notes', 'due_date']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class PaymentForm(StyledModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'method', 'transaction_ref', 'received_on']
        widgets = {'received_on': forms.DateInput(attrs={'type': 'date'})}


class ProjectForm(StyledModelForm):
    class Meta:
        model = Project
        fields = ['name', 'client', 'proposal', 'site_location', 'status',
                  'crew_lead', 'start_date', 'target_end_date', 'completed_on',
                  'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'target_end_date': forms.DateInput(attrs={'type': 'date'}),
            'completed_on': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ProjectNoteForm(StyledModelForm):
    class Meta:
        model = ProjectNote
        fields = ['date', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Progress update…'}),
        }


def _item_formset(parent, item_model):
    return inlineformset_factory(
        parent, item_model,
        fields=['description', 'quantity', 'unit', 'unit_price'],
        widgets={
            'description': forms.TextInput(attrs={'class': 'dash-input',
                                                  'placeholder': 'Description'}),
            'quantity': forms.NumberInput(attrs={'class': 'dash-input', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'dash-input', 'placeholder': 'm / pcs / lot'}),
            'unit_price': forms.NumberInput(attrs={'class': 'dash-input', 'step': '0.01',
                                                   'placeholder': 'KES'}),
        },
        extra=1, can_delete=True)


ProposalItemFormSet = _item_formset(Proposal, ProposalItem)
InvoiceItemFormSet = _item_formset(Invoice, InvoiceItem)
