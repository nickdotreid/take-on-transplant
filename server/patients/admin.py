from django.contrib import admin

from admin_ordering.admin import OrderableAdmin

from .models import Patient
from .models import Attribute
from .models import PatientAttribute
from .models import PatientStory
from .models import PatientStoryHighlight

class PatientStoryHighlightAdminInline(OrderableAdmin, admin.StackedInline):
    model = PatientStoryHighlight
    ordering_field = 'order'

    fields = [
        'order',
        'published',
        'title',
        'content'
    ]

class PatientStoryAdminInline(OrderableAdmin, admin.StackedInline):
    model = PatientStory
    ordering_field = 'order'
    show_change_link = True

    fields = [
        'title',
        'order',
        'published'
    ]

class PatientAttributeAdminInline(OrderableAdmin, admin.TabularInline):
    model = PatientAttribute
    ordering_field = 'order'

    fields = [
        'attribute',
        'value'
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
        PatientAttributeAdminInline,
        PatientStoryHighlightAdminInline,
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

@admin.register(Attribute)
class AttributeAdmin(OrderableAdmin, admin.ModelAdmin):
    ordering_field = "order"
    # ordering_field_hide_input = True

    list_display = ['name', 'order', 'published']
    list_editable = ['order', 'published']
    fields = ['name', 'order', 'published']
