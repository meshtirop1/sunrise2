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