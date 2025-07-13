from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import HttpResponse

from .forms import ContactForm
from .models import Service, ProcessStep, WhyChooseItem, ServicesCTA, GalleryCategory, GalleryItem, GalleryStat, \
    ContactPageContent, ContactSubmission


def home(request):
    """Home page view"""
    return render(request, 'main/home.html')

def about(request):
    """About page view"""
    return render(request, 'main/about.html')


def team(request):
    """About page view"""
    return render(request, 'main/team.html')
def services(request):
    """Services page view"""
    services = Service.objects.all()
    process_steps = ProcessStep.objects.all()
    why_choose_items = WhyChooseItem.objects.all()
    cta = ServicesCTA.objects.first() or ServicesCTA.objects.create()

    context = {
        'services': services,
        'process_steps': process_steps,
        'why_choose_items': why_choose_items,
        'cta': cta,
    }
    return render(request, 'main/services.html', context)
def gallery(request):
    """Gallery page view"""
    categories = GalleryCategory.objects.all()
    gallery_items = GalleryItem.objects.all()
    stats = GalleryStat.objects.all()

    context = {
        'categories': categories,
        'gallery_items': gallery_items,
        'stats': stats,
    }
    return render(request, 'main/gallery.html', context)


def contact(request):
    """Contact page view"""
    content = ContactPageContent.objects.first() or ContactPageContent.objects.create()
    form = ContactForm()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save submission to database
            submission = ContactSubmission.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                inquiry_type=form.cleaned_data['inquiry_type'],
                message=form.cleaned_data['message']
            )

            # Send email to admin
            subject = f"New Contact Form Submission from {form.cleaned_data['name']}"
            email_message = f"""
            New contact form submission:
            Name: {form.cleaned_data['name']}
            Email: {form.cleaned_data['email']}
            Phone: {form.cleaned_data['phone']}
            Inquiry Type: {form.cleaned_data['inquiry_type']}
            Message: {form.cleaned_data['message']}
            """
            try:
                send_mail(
                    subject,
                    email_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
            except Exception as e:
                return render(request, 'main/contact.html', {
                    'content': content,
                    'form': form,
                    'success': False,
                    'message': f"Error sending email: {str(e)}"
                })

            return render(request, 'main/contact.html', {
                'content': content,
                'form': form,
                'success': True,
                'message': 'Thank you for your inquiry. We will get back to you soon!'
            })

    return render(request, 'main/contact.html', {'content': content, 'form': form})