from django.contrib import admin

from admin_ordering.admin import OrderableAdmin

from .models import Patient
from .models import Property
from .models import PatientProperty
from .models import PatientStory

class PatientStoryAdminInline(OrderableAdmin, admin.StackedInline):
    model = PatientStory
    ordering_field = 'order'
    show_change_link = True

    fields = [
        'title',
        'order',
        'published',
        'excerpt'
    ]

class PatientPropertyAdminInline(OrderableAdmin, admin.StackedInline):
    model = PatientProperty
    ordering_field = 'order'

    fields = [
        'property',
        'order',
        'value',
        'published'
    ]

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    filter_horizontal = ['tags']
    order = ['name']

    fields = [
        'name',
        'photo',
        'published',
        'tags'
    ]

    inlines = [
        PatientPropertyAdminInline,
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
        'excerpt',
        'content'
    ]

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    order = ['name']
    fields = ['name']
