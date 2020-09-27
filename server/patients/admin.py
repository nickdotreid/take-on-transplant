from django.contrib import admin

from admin_ordering.admin import OrderableAdmin

from .models import Patient
from .models import PatientStory

class PatientStoryAdminInline(OrderableAdmin, admin.StackedInline):
    model = PatientStory
    ordering_field = 'order'
    show_change_link = True

    fields = [
        'title',
        'order',
        'published'
    ]

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):

    order = ['name']

    fields = [
        'name',
        'published'
    ]

    inlines = [
        PatientStoryAdminInline
    ]

@admin.register(PatientStory)
class PatientStoryAdmin(admin.ModelAdmin):

    order = ['patient_id','title','order']

    list_display = [
        'title',
        'patient',
        'published'
    ]

    fields = [
        'patient',
        'title',
        'order',
        'published',
        'content'
    ]

