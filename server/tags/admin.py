from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from admin_ordering.admin import OrderableAdmin

from .models import Tag
from .models import TagCategory
from .models import TaggedContent

class TaggedContentInline(GenericTabularInline):
    model = TaggedContent
    extra = 0

@admin.register(TagCategory)
class TagCategoryAdmin(OrderableAdmin, admin.ModelAdmin):
    ordering_field = "order"

    list_display = ['name', 'order', 'published']
    list_editable = ['order', 'published']
    fields = ['name', 'order', 'published']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    order = ['name']

    fields = [
        'name',
        'published',
        'category'
    ]

    list_fields = [
        'name',
        'published',
        'category'
    ]
