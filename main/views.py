from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.http import HttpResponse

from .forms import ContactForm
from .models import (Service, ProcessStep, WhyChooseItem, ServicesCTA, GalleryCategory,
    GalleryItem, GalleryStat, ContactPageContent, ContactSubmission, TeamMember,
    HomePageContent, QuickLink, HomeServiceCard, AboutPageContent, TimelineEvent,
    ValueCard, ServicesPageContent, GalleryPageContent, TeamPageContent, InquiryType, FAQ)


def home(request):
    """Home page view"""
    return render(request, 'main/home.html', {
        'content': HomePageContent.load(),
        'about': AboutPageContent.load(),
        'services': Service.objects.exclude(image='')[:6],
        'stats': GalleryStat.objects.all(),
    })

def about(request):
    """About page view"""
    return render(request, 'main/about.html', {
        'content': AboutPageContent.load(),
        'timeline_events': TimelineEvent.objects.all(),
        'values': ValueCard.objects.filter(section='value'),
        'certifications': ValueCard.objects.filter(section='certification'),
    })


def team(request):
    """Team page view"""
    return render(request, 'main/team.html', {
        'content': TeamPageContent.load(),
        'team_members': TeamMember.objects.all(),
    })
def services(request):
    """Services page view"""
    services = Service.objects.all()
    process_steps = ProcessStep.objects.all()
    why_choose_items = WhyChooseItem.objects.all()
    cta = ServicesCTA.objects.first() or ServicesCTA.objects.create()

    context = {
        'content': ServicesPageContent.load(),
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
        'content': GalleryPageContent.load(),
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
    extra = {
        'inquiry_types': InquiryType.objects.all(),
        'faqs': FAQ.objects.all(),
    }

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
                **extra,
            })

    return render(request, 'main/contact.html', {'content': content, 'form': form, **extra})


def robots_txt(request):
    """robots.txt pointing crawlers at the sitemap."""
    sitemap_url = request.build_absolute_uri('/sitemap.xml')
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /dashboard/",
        "Allow: /",
        "",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    """Simple XML sitemap of the public pages."""
    from django.urls import reverse
    pages = [
        ('main:home', '1.0', 'weekly'),
        ('main:services', '0.9', 'monthly'),
        ('main:about', '0.8', 'monthly'),
        ('main:gallery', '0.8', 'monthly'),
        ('main:team', '0.6', 'monthly'),
        ('main:contact', '0.9', 'monthly'),
    ]
    items = []
    for name, priority, freq in pages:
        loc = request.build_absolute_uri(reverse(name))
        items.append(
            f"<url><loc>{loc}</loc><changefreq>{freq}</changefreq>"
            f"<priority>{priority}</priority></url>"
        )
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           + "".join(items) + '</urlset>')
    return HttpResponse(xml, content_type="application/xml")
