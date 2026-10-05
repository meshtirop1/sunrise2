from django.contrib import admin
from .models import (ProcessStep, WhyChooseItem, ServicesCTA, Service, GalleryItem, GalleryCategory, GalleryStat, TeamMember,
                     ContactPageContent, ContactSubmission,
                     SiteSettings, HomePageContent, QuickLink, HomeServiceCard,
                     AboutPageContent, TimelineEvent, ValueCard, ServicesPageContent,
                     GalleryPageContent, TeamPageContent, InquiryType, FAQ)
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


# --- Editable page content -------------------------------------------------

class SingletonAdmin(admin.ModelAdmin):
    """One-row content models: no add/delete, jump straight to the edit form."""
    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect
        obj = self.model.load()
        return redirect(f'./{obj.pk}/change/')


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    fieldsets = (
        ('Contact details', {'fields': ('email', 'phone_primary', 'phone_secondary',
                                        'physical_address', 'postal_address', 'website')}),
        ('Business hours', {'fields': ('business_hours',)}),
        ('Map', {'fields': ('map_embed_url', 'map_title', 'map_address')}),
        ('Social media', {'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'tiktok_url')}),
        ('Footer', {'fields': ('copyright_text',)}),
    )


@admin.register(HomePageContent)
class HomePageContentAdmin(SingletonAdmin):
    pass


@admin.register(AboutPageContent)
class AboutPageContentAdmin(SingletonAdmin):
    pass


@admin.register(ServicesPageContent)
class ServicesPageContentAdmin(SingletonAdmin):
    pass


@admin.register(GalleryPageContent)
class GalleryPageContentAdmin(SingletonAdmin):
    pass


@admin.register(TeamPageContent)
class TeamPageContentAdmin(SingletonAdmin):
    pass


@admin.register(QuickLink)
class QuickLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'page', 'icon', 'order')
    list_editable = ('order',)


@admin.register(HomeServiceCard)
class HomeServiceCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'description')


@admin.register(TimelineEvent)
class TimelineEventAdmin(admin.ModelAdmin):
    list_display = ('year', 'title', 'order')
    list_editable = ('order',)


@admin.register(ValueCard)
class ValueCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'icon', 'order')
    list_filter = ('section',)
    list_editable = ('order',)


@admin.register(InquiryType)
class InquiryTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order')
    list_editable = ('order',)
    search_fields = ('question', 'answer')
