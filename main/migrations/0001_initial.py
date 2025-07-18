# Generated by Django 5.2.4 on 2025-07-13 06:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ContactPageContent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(default="Contact Us", max_length=200)),
                (
                    "subtitle",
                    models.TextField(
                        default="Get in touch with us for inquiries, quotes, or support"
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Contact Page Content",
                "verbose_name_plural": "Contact Page Content",
            },
        ),
        migrations.CreateModel(
            name="ContactSubmission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("inquiry_type", models.CharField(blank=True, max_length=100)),
                ("message", models.TextField()),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("is_processed", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Contact Submission",
                "verbose_name_plural": "Contact Submissions",
                "ordering": ["-submitted_at"],
            },
        ),
        migrations.CreateModel(
            name="GalleryCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "slug",
                    models.SlugField(
                        help_text="Used for filtering, e.g., 'dams'",
                        max_length=100,
                        unique=True,
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="gallery/categories/"
                    ),
                ),
                (
                    "project_count",
                    models.CharField(
                        blank=True,
                        help_text="e.g., '15+ Projects Completed'",
                        max_length=50,
                    ),
                ),
                ("order", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Gallery Category",
                "verbose_name_plural": "Gallery Categories",
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="GalleryStat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("number", models.CharField(help_text="e.g., '90+'", max_length=50)),
                (
                    "label",
                    models.CharField(
                        help_text="e.g., 'Projects Completed'", max_length=100
                    ),
                ),
                ("order", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Gallery Statistic",
                "verbose_name_plural": "Gallery Statistics",
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="ProcessStep",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("order", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Process Step",
                "verbose_name_plural": "Process Steps",
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="Service",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="services/images/"
                    ),
                ),
                (
                    "features",
                    models.TextField(
                        help_text="Enter features as a comma-separated list"
                    ),
                ),
                (
                    "primary_cta_text",
                    models.CharField(default="Get Quote", max_length=50),
                ),
                (
                    "primary_cta_url",
                    models.CharField(default="main:contact", max_length=200),
                ),
                (
                    "secondary_cta_text",
                    models.CharField(default="View Projects", max_length=50),
                ),
                (
                    "secondary_cta_url",
                    models.CharField(default="main:gallery", max_length=200),
                ),
                ("order", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Service",
                "verbose_name_plural": "Services",
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="ServicesCTA",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(default="Ready to Get Started?", max_length=200),
                ),
                (
                    "subtitle",
                    models.TextField(
                        default="Contact us today for a free consultation and quote for your project"
                    ),
                ),
                (
                    "primary_cta_text",
                    models.CharField(default="Get Free Quote", max_length=50),
                ),
                (
                    "primary_cta_url",
                    models.CharField(default="main:contact", max_length=200),
                ),
                (
                    "secondary_cta_text",
                    models.CharField(default="View Our Work", max_length=50),
                ),
                (
                    "secondary_cta_url",
                    models.CharField(default="main:gallery", max_length=200),
                ),
            ],
            options={
                "verbose_name": "Services CTA",
                "verbose_name_plural": "Services CTA",
            },
        ),
        migrations.CreateModel(
            name="WhyChooseItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                (
                    "icon",
                    models.CharField(
                        help_text="Font Awesome icon class, e.g., fa-clock",
                        max_length=100,
                    ),
                ),
                ("order", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Why Choose Item",
                "verbose_name_plural": "Why Choose Items",
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="GalleryItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("image", models.ImageField(upload_to="gallery/images/")),
                ("order", models.PositiveIntegerField(default=0)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="main.gallerycategory",
                    ),
                ),
            ],
            options={
                "verbose_name": "Gallery Item",
                "verbose_name_plural": "Gallery Items",
                "ordering": ["order"],
            },
        ),
    ]
