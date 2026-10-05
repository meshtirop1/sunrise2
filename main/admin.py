from django.contrib import admin
from .models import (ProcessStep, WhyChooseItem, ServicesCTA, Service, GalleryItem, GalleryCategory, GalleryStat, TeamMember,
                     ContactPageContent, ContactSubmission)
# Register your models here.
#Admin configuration
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    search_fields = ('title', 'description')
    list_editable = ('order',)

@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    search_fields = ('title', 'description')
    list_editable = ('order',)

@admin.register(WhyChooseItem)
class WhyChooseItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    search_fields = ('title', 'description')
    list_editable = ('order',)

@admin.register(ServicesCTA)
class ServicesCTAAdmin(admin.ModelAdmin):
    list_display = ('title',)

@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)

@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'order')
    search_fields = ('title', 'description')
    list_filter = ('category',)
    list_editable = ('order',)

@admin.register(GalleryStat)
class GalleryStatAdmin(admin.ModelAdmin):
    list_display = ('number', 'label', 'order')
    search_fields = ('label',)
    list_editable = ('order',)

@admin.register(ContactPageContent)
class ContactPageContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'updated_at')
    search_fields = ('title', 'subtitle')

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'inquiry_type', 'submitted_at', 'is_processed')
    list_filter = ('is_processed', 'inquiry_type')
    search_fields = ('name', 'email', 'message')
    list_editable = ('is_processed',)


# "Convert enquiry to client" action: creates a business.Client from a
# contact submission so staff can immediately write them a proposal.
def create_client_from_enquiry(modeladmin, request, queryset):
    from business.models import Client
    created, existing = 0, 0
    for sub in queryset:
        _, was_created = Client.objects.get_or_create(
            email=sub.email,
            defaults={'name': sub.name, 'phone': sub.phone,
                      'notes': f"Created from website enquiry of {sub.submitted_at:%d %b %Y}:\n{sub.message}"},
        )
        created += was_created
        existing += (not was_created)
        if not sub.is_processed:
            sub.is_processed = True
            sub.save(update_fields=['is_processed'])
    msg = f"{created} client(s) created."
    if existing:
        msg += f" {existing} already existed (matched by email)."
    modeladmin.message_user(request, msg + " Enquiries marked as processed.")


create_client_from_enquiry.short_description = "Create client from enquiry (and mark processed)"
ContactSubmissionAdmin.actions = [create_client_from_enquiry]


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'phone', 'email', 'order')
    list_editable = ('order',)
    search_fields = ('name', 'role')
