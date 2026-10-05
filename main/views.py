from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import HttpResponse

from .forms import ContactForm
from .models import Service, ProcessStep, WhyChooseItem, ServicesCTA, GalleryCategory, GalleryItem, GalleryStat, \
    ContactPageContent, ContactSubmission, TeamMember


def home(request):
    """Home page view"""
    return render(request, 'main/home.html')

def about(request):
    """About page view"""
    return render(request, 'main/about.html')


def team(request):
    """Team page view"""
    return render(request, 'main/team.html', {'team_members': TeamMember.objects.all()})
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
    """Contact page view: saves the enquiry, notifies the company inbox and
    sends the visitor a branded auto-reply."""
    content = ContactPageContent.objects.first() or ContactPageContent.objects.create()
    form = ContactForm()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            ContactSubmission.objects.create(
                name=data['name'], email=data['email'], phone=data['phone'],
                inquiry_type=data['inquiry_type'], message=data['message'],
            )

            company = settings.COMPANY_INFO
            # Notify the company inbox. Email failures are logged but never
            # shown to the visitor - the enquiry is already saved above.
            try:
                send_mail(
                    f"New website enquiry from {data['name']} ({data['inquiry_type'] or 'General'})",
                    (f"Name: {data['name']}\nEmail: {data['email']}\nPhone: {data['phone']}\n"
                     f"Inquiry Type: {data['inquiry_type']}\n\nMessage:\n{data['message']}\n\n"
                     f"Reply directly to this email to answer the client."),
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
                # Auto-reply to the visitor.
                send_mail(
                    f"We received your enquiry – {company['name']}",
                    (f"Dear {data['name']},\n\n"
                     f"Thank you for contacting {company['name']}. We have received your "
                     f"enquiry and one of our team "
                     f"will get back to you within one business day.\n\n"
                     f"In the meantime, you can reach us directly on "
                     f"{' or '.join(company['phones'])}.\n\n"
                     f"Kind regards,\n{company['name']}\n{company['address']}\n{company['website']}"),
                    settings.DEFAULT_FROM_EMAIL,
                    [data['email']],
                    fail_silently=True,
                )
            except Exception:
                pass

            return render(request, 'main/contact.html', {
                'content': content,
                'form': ContactForm(),
                'success': True,
                'message': 'Thank you for your enquiry. A confirmation email has been sent to you '
                           'and our team will get back to you shortly!',
            })

    return render(request, 'main/contact.html', {'content': content, 'form': form})
