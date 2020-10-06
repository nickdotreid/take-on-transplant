from django.contrib import admin

from .models import Resource

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):

    order = ['name']

    list_fields = [
        'name',
        'published'
    ]

    fields = [
        'name',
        'published',
        'description',
        'content'
    ]
