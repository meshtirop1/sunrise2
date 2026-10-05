# Contact form
from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    # Free text so it always matches the dropdown, whose options are managed
    # in the admin (InquiryType model).
    inquiry_type = forms.CharField(max_length=100, required=False)
    message = forms.CharField(widget=forms.Textarea, required=True)
