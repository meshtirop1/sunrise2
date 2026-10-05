"""Make site-wide editable content available to every template."""
from .models import Service, SiteSettings


def site_content(request):
    return {
        'site_settings': SiteSettings.load(),
        'footer_services': Service.objects.all()[:6],
    }
