# Contact form
from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    inquiry_type = forms.ChoiceField(
        choices=[
            ('General Inquiry', 'General Inquiry'),
            ('Drilling Services', 'Drilling Services'),
            ('Dam Construction', 'Dam Construction'),
            ('Water Surveys', 'Water Surveys'),
            ('Geological Surveys', 'Geological Surveys'),
            ('Transport and Logistics', 'Transport and Logistics'),
            ('General Supplies', 'General Supplies'),
        ],
        required=False
    )
    message = forms.CharField(widget=forms.Textarea, required=True)