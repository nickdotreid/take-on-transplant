from django.contrib import admin

from admin_ordering.admin import OrderableAdmin

from tags.admin import TaggedContentInline

from .models import Article
from .models import Definition
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

@admin.register(Definition)
class DefinitionAdmin(admin.ModelAdmin):

    order = ['name']

    list_fields = [
        'name',
        'published'
    ]

    fields = [
        'name',
        'published',
        'description'
    ]

class ArticleAdminInline(OrderableAdmin, admin.StackedInline):
    model = Article
    ordering_field = 'order'
    show_change_link = True

    fields = [
        'title',
        'order',
        'published'
    ]

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):

    order = [
        'parent',
        'order'
    ]

    list_filter = [
        'published'
    ]

    list_display = [
        'title',
        'parent',
        'published'
    ]

    inlines = [
        TaggedContentInline,
        ArticleAdminInline
    ]
