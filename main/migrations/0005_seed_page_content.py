# Seed the editable page content with the wording the templates used to
# hard-code, so the site looks identical after the switch.
from django.db import migrations

QUICK_LINKS = [
    ("fa-users", "Who we are", "Learn about our company", "main:about"),
    ("fa-cogs", "Services", "Explore our offerings", "main:services"),
    ("fa-images", "Gallery", "View our projects", "main:gallery"),
    ("fa-envelope", "Reach us", "Get in touch today", "main:contact"),
]

HOME_CARDS = [
    ("fa-water", "Construction of Dams",
     "We specialize in constructing durable dams to store and manage water resources, "
     "ensuring long-term sustainability for communities and industries."),
    ("fa-oil-well", "Drilling of Boreholes",
     "Our borehole drilling services provide reliable access to clean groundwater, helping "
     "households, businesses, and agricultural projects meet their water needs."),
    ("fa-tint", "Construction of Water Pans",
     "We build high-quality water pans to collect and store rainwater, supporting irrigation, "
     "livestock, and domestic water supply."),
    ("fa-truck", "Transport and Logistics",
     "Our transport and logistics services ensure the efficient movement of goods and materials, "
     "providing seamless supply chain solutions."),
    ("fa-boxes", "General Supplies",
     "We supply high-quality construction materials, equipment, and essential goods, ensuring "
     "businesses and projects have what they need to succeed."),
    ("fa-search", "Water Surveys & Consultancy",
     "Our consultancy services offer expert water surveys and assessments, helping clients make "
     "informed decisions about water resource management."),
]

ABOUT_INTRO = (
    "SUNRISE DRILLING LIMITED has been a trusted provider of construction and general supply "
    "services since 2019. Over the years, the company has expanded its reach to meet the evolving "
    "needs of modern businesses. With a strategic location in Eldoret, Uasin Gishu County, and an "
    "extensive network across Kenya and East African countries, the company has successfully "
    "undertaken various construction and logistical projects."
)

MISSION = (
    "SUNRISE DRILLING LIMITED strives to be a creative and innovative leader in the construction "
    "and general supplies industry. We are dedicated to enhancing efficiency, improving "
    "reliability, and exploring new methodologies to provide the best possible service to "
    "clients. Through continuous improvement, innovative approaches, and a customer-centric "
    "focus, we aim to transcend industry standards and establish ourselves as a prominent "
    "business moving forward."
)

VISION = (
    "To be the leading provider of water solutions and construction services in East Africa, "
    "recognized for our commitment to quality, innovation, and sustainable development. We "
    "envision a future where every community has access to reliable water resources through our "
    "expert drilling and construction services."
)

CERT_INTRO = (
    "SUNRISE DRILLING LIMITED is committed to upholding the highest standards in management, "
    "administration, and service delivery. The company ensures strict compliance with "
    "international standards, including those set by the International Organization for "
    "Standardization (ISO). Furthermore, all operations adhere to the Kenya Bureau of Standards "
    "(KEBS), reinforcing a commitment to quality and regulatory compliance. This dedication "
    "guarantees that clients receive services that meet both national and international "
    "benchmarks."
)

TIMELINE = [
    ("2019", "Company Founded", "fa-rocket",
     "SUNRISE DRILLING LIMITED was established with a vision to provide reliable construction "
     "and drilling services in Kenya."),
    ("2020", "Regional Expansion", "fa-expand-arrows-alt",
     "Expanded our services across Kenya and began operations in neighboring East African countries."),
    ("2021", "ISO Certification", "fa-certificate",
     "Achieved ISO certification and KEBS compliance, reinforcing our commitment to quality and "
     "regulatory standards."),
    ("2022-2025", "Continued Excellence", "fa-award",
     "Continued to deliver exceptional services while maintaining our position as a reliable "
     "name in the drilling and construction industry."),
]

VALUES = [
    ("fa-handshake", "Integrity",
     "We conduct our business with honesty, transparency, and ethical practices in all our "
     "interactions with clients and partners."),
    ("fa-lightbulb", "Innovation",
     "We continuously explore new methodologies and technologies to provide cutting-edge "
     "solutions for our clients' needs."),
    ("fa-heart", "Customer Satisfaction",
     "Our clients' success is our priority. We deliver personalized service and cost-effective "
     "solutions for every project."),
    ("fa-medal", "Excellence",
     "We maintain the highest standards in all our services, ensuring quality and reliability "
     "in every project we undertake."),
    ("fa-users", "Social Responsibility",
     "We actively empower youth and individuals with disabilities, contributing to a more "
     "inclusive and progressive society."),
    ("fa-leaf", "Sustainability",
     "We are committed to environmentally responsible practices and sustainable water resource "
     "management."),
]

CERTIFICATIONS = [
    ("fa-globe", "ISO Standards",
     "Certified to meet International Organization for Standardization requirements for quality "
     "management systems."),
    ("fa-flag", "KEBS Compliance",
     "Full compliance with Kenya Bureau of Standards for all our operations and service delivery."),
    ("fa-shield-alt", "Safety Standards",
     "Adherence to international safety protocols and best practices in all our drilling and "
     "construction activities."),
]

INQUIRY_TYPES = [
    "Construction of Dams", "Construction of Water Pans", "Drilling of Boreholes",
    "Transport and Logistics", "General Supplies", "Water Surveys and Consultancy",
    "Plumbing Works", "Customer Support",
]

FAQS = [
    ("What types of drilling services do you offer?",
     "We offer comprehensive drilling services including water borehole drilling, dam "
     "construction, water pan construction, and water surveys. Our services cover both "
     "residential and commercial projects across Kenya and East Africa."),
    ("How long does it take to complete a borehole project?",
     "The duration depends on various factors including depth, ground conditions, and location "
     "accessibility. Typically, a standard borehole takes 3-7 days to complete, including "
     "drilling, installation, and testing."),
    ("Do you provide maintenance services?",
     "Yes, we provide comprehensive maintenance and repair services for all our installations. "
     "We offer regular maintenance contracts and emergency repair services to ensure your water "
     "systems operate efficiently."),
    ("What areas do you serve?",
     "We serve all regions across Kenya and have expanded our operations to neighboring East "
     "African countries. Our headquarters in Eldoret allows us to efficiently serve the entire "
     "region."),
    ("Are you licensed and insured?",
     "Yes, we are fully licensed and certified. We comply with ISO standards and Kenya Bureau "
     "of Standards (KEBS) requirements. We carry comprehensive insurance coverage for all our "
     "operations."),
]

MAP_EMBED = ("https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3989.6645282159516!2d35.26347160000001"
             "!3d0.5030712715775137!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x17810164fd2d5b45"
             "%3A0x179f30e244580ae8!2sSunrise%20Drilling%20Company!5e0!3m2!1sen!2skr!4v1752392269568!5m2!1sen!2skr")


def seed(apps, schema_editor):
    SiteSettings = apps.get_model('main', 'SiteSettings')
    ss, _ = SiteSettings.objects.get_or_create(pk=1)
    if not ss.map_embed_url:
        ss.map_embed_url = MAP_EMBED
        ss.save()

    for model_name in ('HomePageContent', 'ServicesPageContent',
                       'GalleryPageContent', 'TeamPageContent'):
        apps.get_model('main', model_name).objects.get_or_create(pk=1)

    About = apps.get_model('main', 'AboutPageContent')
    about, _ = About.objects.get_or_create(pk=1)
    if not about.intro:
        about.intro = ABOUT_INTRO
        about.mission_text = MISSION
        about.vision_text = VISION
        about.cert_intro = CERT_INTRO
        about.save()

    QuickLink = apps.get_model('main', 'QuickLink')
    if not QuickLink.objects.exists():
        for i, (icon, title, desc, page) in enumerate(QUICK_LINKS, 1):
            QuickLink.objects.create(icon=icon, title=title, description=desc, page=page, order=i)

    HomeServiceCard = apps.get_model('main', 'HomeServiceCard')
    if not HomeServiceCard.objects.exists():
        for i, (icon, title, desc) in enumerate(HOME_CARDS, 1):
            HomeServiceCard.objects.create(icon=icon, title=title, description=desc, order=i)

    TimelineEvent = apps.get_model('main', 'TimelineEvent')
    if not TimelineEvent.objects.exists():
        for i, (year, title, icon, desc) in enumerate(TIMELINE, 1):
            TimelineEvent.objects.create(year=year, title=title, icon=icon, description=desc, order=i)

    ValueCard = apps.get_model('main', 'ValueCard')
    if not ValueCard.objects.exists():
        for i, (icon, title, desc) in enumerate(VALUES, 1):
            ValueCard.objects.create(section='value', icon=icon, title=title, description=desc, order=i)
        for i, (icon, title, desc) in enumerate(CERTIFICATIONS, 1):
            ValueCard.objects.create(section='certification', icon=icon, title=title,
                                     description=desc, order=i)

    InquiryType = apps.get_model('main', 'InquiryType')
    if not InquiryType.objects.exists():
        for i, name in enumerate(INQUIRY_TYPES, 1):
            InquiryType.objects.create(name=name, order=i)

    FAQ = apps.get_model('main', 'FAQ')
    if not FAQ.objects.exists():
        for i, (q, a) in enumerate(FAQS, 1):
            FAQ.objects.create(question=q, answer=a, order=i)


def unseed(apps, schema_editor):
    for name in ('QuickLink', 'HomeServiceCard', 'TimelineEvent', 'ValueCard',
                 'InquiryType', 'FAQ'):
        apps.get_model('main', name).objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0004_aboutpagecontent_faq_gallerypagecontent_and_more'),
    ]
    operations = [
        migrations.RunPython(seed, unseed),
    ]
