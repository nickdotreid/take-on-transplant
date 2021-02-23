from django.contrib import admin

from admin_ordering.admin import OrderableAdmin

from tags.admin import TaggedContentInline

from .models import Author
from .models import Category
from .models import FrequentlyAskedQuestion
from .models import Answer
from .models import QuestionInCategory
from .models import FAQHighlight

class AnswerAdminInline(OrderableAdmin, admin.StackedInline):
    model = Answer
    ordering_field = 'order'

    fields = [
        'order',
        'author',
        'published',
        'text'
    ]

class FAQHighlightAdminInline(OrderableAdmin, admin.StackedInline):
    model = FAQHighlight
    ordering_field = 'order'

    fields = [
        'order',
        'published',
        'title',
        'content'
    ]

@admin.register(FrequentlyAskedQuestion)
class FrequentlyAskedQuestionAdmin(admin.ModelAdmin):
    order = ['text']

    inlines = [
        TaggedContentInline,
        FAQHighlightAdminInline,
        AnswerAdminInline
    ]

class QuestionInCategoryAdminInline(OrderableAdmin, admin.StackedInline):
    model = QuestionInCategory
    ordering_field = 'order'

    fields = [
        'order',
        'question'
    ]

@admin.register(Category)
class CategoryAdmin(OrderableAdmin, admin.ModelAdmin):
    ordering_field="order"

    list_display = ['name', 'order', 'published']
    list_editable = ['order', 'published']

    inlines = [
        QuestionInCategoryAdminInline
    ]

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    pass
