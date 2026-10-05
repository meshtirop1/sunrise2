from django.db import models
from django.shortcuts import render
from django.contrib import admin

# Model for individual services
class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='services/images/', blank=True, null=True)
    features = models.TextField(help_text="Enter features as a comma-separated list")
    primary_cta_text = models.CharField(max_length=50, default="Get Quote")
    primary_cta_url = models.CharField(max_length=200, default="main:contact")
    secondary_cta_text = models.CharField(max_length=50, default="View Projects")
    secondary_cta_url = models.CharField(max_length=200, default="main:gallery")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['order']

    def __str__(self):
        return self.title

    def get_features_list(self):
        return [feature.strip() for feature in self.features.split(',')]

# Model for process steps
class ProcessStep(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Process Step"
        verbose_name_plural = "Process Steps"
        ordering = ['order']

    def __str__(self):
        return self.title

# Model for why choose us items
class WhyChooseItem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100, help_text="Font Awesome icon class, e.g., fa-clock")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Why Choose Item"
        verbose_name_plural = "Why Choose Items"
        ordering = ['order']

    def __str__(self):
        return self.title

# Model for CTA section
class ServicesCTA(models.Model):
    title = models.CharField(max_length=200, default="Ready to Get Started?")
    subtitle = models.TextField(default="Contact us today for a free consultation and quote for your project")
    primary_cta_text = models.CharField(max_length=50, default="Get Free Quote")
    primary_cta_url = models.CharField(max_length=200, default="main:contact")
    secondary_cta_text = models.CharField(max_length=50, default="View Our Work")
    secondary_cta_url = models.CharField(max_length=200, default="main:gallery")

    class Meta:
        verbose_name = "Services CTA"
        verbose_name_plural = "Services CTA"

    def __str__(self):
        return self.title

class GalleryCategory(models.Model):
        name = models.CharField(max_length=100, unique=True)
        slug = models.SlugField(max_length=100, unique=True, help_text="Used for filtering, e.g., 'dams'")
        image = models.ImageField(upload_to='gallery/categories/', blank=True, null=True)
        project_count = models.CharField(max_length=50, blank=True, help_text="e.g., '15+ Projects Completed'")
        order = models.PositiveIntegerField(default=0)

        class Meta:
            verbose_name = "Gallery Category"
            verbose_name_plural = "Gallery Categories"
            ordering = ['order']

        def __str__(self):
            return self.name

    # Model for gallery items
class GalleryItem(models.Model):
        category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE, related_name='items')
        title = models.CharField(max_length=200)
        description = models.TextField()
        image = models.ImageField(upload_to='gallery/images/')
        order = models.PositiveIntegerField(default=0)

        class Meta:
            verbose_name = "Gallery Item"
            verbose_name_plural = "Gallery Items"
            ordering = ['order']

        def __str__(self):
            return self.title

    # Model for gallery statistics
class GalleryStat(models.Model):
        number = models.CharField(max_length=50, help_text="e.g., '90+'")
        label = models.CharField(max_length=100, help_text="e.g., 'Projects Completed'")
        order = models.PositiveIntegerField(default=0)

        class Meta:
            verbose_name = "Gallery Statistic"
            verbose_name_plural = "Gallery Statistics"
            ordering = ['order']

        def __str__(self):
            return f"{self.number} {self.label}"


class ContactPageContent(models.Model):
    title = models.CharField(max_length=200, default="Contact Us")
    subtitle = models.TextField(default="Get in touch with us for inquiries, quotes, or support")
    form_title = models.CharField(max_length=200, default="Send Us a Message")
    form_subtitle = models.CharField(
        max_length=255,
        default="Please fill the form below and we will get back to you as soon as possible")
    email_note = models.CharField(max_length=255, default="We respond to all emails within 24 hours")
    phone_note = models.CharField(max_length=255, default="Available 24/7 for emergency services")
    map_section_title = models.CharField(max_length=200, default="Find Us")
    map_section_subtitle = models.CharField(max_length=255, default="Our location in Eldoret, Kenya")
    faq_title = models.CharField(max_length=200, default="Frequently Asked Questions")
    faq_subtitle = models.CharField(max_length=255, default="Common questions about our services")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contact Page Content"
        verbose_name_plural = "Contact Page Content"

    def __str__(self):
        return self.title

# Model for contact form submissions
class ContactSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    inquiry_type = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.name} - {self.email} ({self.submitted_at})"

# Model for team members shown on the Team page (seeded from the company profile)
class TeamMember(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    bio = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"
        ordering = ['order']

    def __str__(self):
        return f"{self.name} – {self.role}"

    def initials(self):
        parts = [p for p in self.name.split() if p and p[0].isalpha()]
        return ''.join(p[0].upper() for p in parts[:2])


# ---------------------------------------------------------------------------
# Editable page content. Every public page reads its text from these models
# so staff can change wording, headings and contact details in the admin
# without touching code.
# ---------------------------------------------------------------------------

class SingletonModel(models.Model):
    """Base for one-row content models. load() always returns the single row."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SiteSettings(SingletonModel):
    """Company-wide contact details shown in the header, footer, home page
    CTA and contact page."""
    email = models.EmailField(default="sunrisedrillingltd@gmail.com")
    phone_primary = models.CharField(max_length=30, default="+254 720 997 769")
    phone_secondary = models.CharField(max_length=30, blank=True, default="+254 728 821 642")
    physical_address = models.CharField(
        max_length=255, default="G737+69Q, Rivatex road, Ndovu lane, Pioneer, Eldoret, Kenya")
    postal_address = models.CharField(max_length=255, default="P.O. BOX 9630-30100, ELDORET")
    website = models.CharField(max_length=100, default="www.sunrisedrillingltd.com")
    business_hours = models.TextField(
        default=("Monday - Friday: 8:00 AM - 6:00 PM\nSaturday: 9:00 AM - 4:00 PM\n"
                 "Sunday: Emergency services only\nEmergency: 24/7 Available"),
        help_text="One line per entry; shown on the contact page")
    map_embed_url = models.TextField(
        blank=True, help_text="Google Maps embed URL for the contact page map")
    map_title = models.CharField(max_length=200, default="Sunrise Drilling Ltd Headquarters")
    map_address = models.TextField(
        default="G737+69Q, Rivatex road, Ndovu lane, Pioneer\nEldoret, Uasin Gishu County, Kenya")
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    copyright_text = models.CharField(max_length=200,
                                      default="Sunrise Drilling. All rights reserved")

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    def business_hours_lines(self):
        return [l.strip() for l in self.business_hours.splitlines() if l.strip()]

    def map_address_lines(self):
        return [l.strip() for l in self.map_address.splitlines() if l.strip()]


class HomePageContent(SingletonModel):
    hero_title = models.CharField(max_length=200, default="Sunrise Drilling")
    hero_subtitle = models.CharField(max_length=200, default="Expert Drilling Services")
    hero_location = models.CharField(max_length=200, default="In Kenya")
    hero_button_text = models.CharField(max_length=50, default="CONTACT US")
    services_title = models.CharField(max_length=200, default="Our Services")
    services_subtitle = models.CharField(max_length=255, default="The areas we are working on are:")
    cta_title = models.CharField(max_length=200, default="Ready to Start Your Project?")
    cta_subtitle = models.CharField(
        max_length=255,
        default="Get in touch with us today for expert drilling services and water solutions")
    cta_button_text = models.CharField(max_length=50, default="Contact Us Today")

    class Meta:
        verbose_name = "Home Page"
        verbose_name_plural = "Home Page"

    def __str__(self):
        return "Home Page Content"


class QuickLink(models.Model):
    """The four shortcut cards under the home hero."""
    PAGE_CHOICES = [
        ('main:home', 'Home'),
        ('main:about', 'Who we are'),
        ('main:team', 'Team'),
        ('main:services', 'Services'),
        ('main:gallery', 'Gallery'),
        ('main:contact', 'Contact'),
    ]
    icon = models.CharField(max_length=50, help_text="Font Awesome class, e.g. fa-users")
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    page = models.CharField(max_length=30, choices=PAGE_CHOICES, default='main:contact')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Home Quick Link"
        verbose_name_plural = "Home Quick Links"
        ordering = ['order']

    def __str__(self):
        return self.title


class HomeServiceCard(models.Model):
    """The service preview cards on the home page."""
    icon = models.CharField(max_length=50, help_text="Font Awesome class, e.g. fa-water")
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Home Service Card"
        verbose_name_plural = "Home Service Cards"
        ordering = ['order']

    def __str__(self):
        return self.title


class AboutPageContent(SingletonModel):
    title = models.CharField(max_length=200, default="About Sunrise Drilling")
    subtitle = models.CharField(
        max_length=255,
        default="Your trusted partner for water solutions and drilling services in Kenya")
    intro = models.TextField(default="")
    journey_title = models.CharField(max_length=200, default="Our Journey")
    journey_subtitle = models.CharField(max_length=255,
                                        default="A timeline of our growth and achievements")
    values_title = models.CharField(max_length=200, default="Our Values")
    values_subtitle = models.CharField(max_length=255,
                                       default="The principles that guide everything we do")
    mission_text = models.TextField(default="")
    vision_text = models.TextField(default="")
    cert_title = models.CharField(max_length=200, default="Certifications and Compliance")
    cert_subtitle = models.CharField(max_length=255,
                                     default="Our commitment to quality and regulatory standards")
    cert_intro = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "About Page"
        verbose_name_plural = "About Page"

    def __str__(self):
        return "About Page Content"


class TimelineEvent(models.Model):
    """An entry in the About page 'Our Journey' timeline."""
    year = models.CharField(max_length=20, help_text="e.g. 2019 or 2022-2025")
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, default="fa-rocket",
                            help_text="Font Awesome class, e.g. fa-rocket")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Timeline Event"
        verbose_name_plural = "Timeline Events"
        ordering = ['order']

    def __str__(self):
        return f"{self.year} – {self.title}"


class ValueCard(models.Model):
    """A card in the About page 'Our Values' or 'Certifications' grids."""
    SECTION_CHOICES = [
        ('value', 'Our Values'),
        ('certification', 'Certifications & Compliance'),
    ]
    section = models.CharField(max_length=20, choices=SECTION_CHOICES, default='value')
    icon = models.CharField(max_length=50, help_text="Font Awesome class, e.g. fa-handshake")
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "About Value / Certification Card"
        verbose_name_plural = "About Value / Certification Cards"
        ordering = ['order']

    def __str__(self):
        return f"{self.get_section_display()}: {self.title}"


class ServicesPageContent(SingletonModel):
    header_title = models.CharField(max_length=200, default="Our Services")
    header_subtitle = models.CharField(
        max_length=255,
        default="Comprehensive solutions for all your drilling, construction, and supply needs")
    intro_title = models.CharField(max_length=255, default="The areas we are working on are:")
    process_title = models.CharField(max_length=200, default="Our Process")
    process_subtitle = models.CharField(
        max_length=255, default="How we deliver exceptional results for every project")
    why_title = models.CharField(max_length=200, default="Why Choose Sunrise Drilling?")
    why_subtitle = models.CharField(max_length=255, default="What sets us apart in the industry")

    class Meta:
        verbose_name = "Services Page"
        verbose_name_plural = "Services Page"

    def __str__(self):
        return "Services Page Content"


class GalleryPageContent(SingletonModel):
    header_title = models.CharField(max_length=200, default="Our Gallery")
    header_subtitle = models.CharField(
        max_length=255,
        default="Explore our portfolio of successful projects and see the quality of our work")
    categories_title = models.CharField(max_length=200, default="Project Categories")
    categories_subtitle = models.CharField(
        max_length=255, default="Explore our diverse range of water solution projects")
    achievements_title = models.CharField(max_length=200, default="Our Achievements")

    class Meta:
        verbose_name = "Gallery Page"
        verbose_name_plural = "Gallery Page"

    def __str__(self):
        return "Gallery Page Content"


class TeamPageContent(SingletonModel):
    header_title = models.CharField(max_length=200, default="Our Team")
    header_subtitle = models.CharField(
        max_length=255, default="The people behind Kenya's trusted water solutions")
    cta_title = models.CharField(max_length=200, default="Want to work with us?")
    cta_subtitle = models.CharField(max_length=255,
                                    default="Talk to our team about your water project today.")

    class Meta:
        verbose_name = "Team Page"
        verbose_name_plural = "Team Page"

    def __str__(self):
        return "Team Page Content"


class InquiryType(models.Model):
    """The options in the contact form 'Inquiry Type' dropdown."""
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Contact Inquiry Type"
        verbose_name_plural = "Contact Inquiry Types"
        ordering = ['order']

    def __str__(self):
        return self.name


class FAQ(models.Model):
    """A question/answer on the contact page."""
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['order']

    def __str__(self):
        return self.question
