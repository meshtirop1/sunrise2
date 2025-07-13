from django.contrib import admin
from .models import (ProcessStep, WhyChooseItem, ServicesCTA, Service, GalleryItem, GalleryCategory, GalleryStat,
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
