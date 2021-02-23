from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Tag
from .models import TaggedContent

class TaggedContentInline(GenericTabularInline):
    model = TaggedContent
    extra = 0

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    order = ['name']

    fields = [
        'name',
        'published'
    ]

    list_fields = [
        'name',
        'published'
    ]
