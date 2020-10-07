from django.contrib import admin

from .models import Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    order = ['name']

    fields = [
        'name',
        'published',
        'warning'
    ]

    list_fields = [
        'name',
        'published',
        'warning'
    ]
