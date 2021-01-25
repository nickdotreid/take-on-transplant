from django.http import Http404
from django.views.generic.base import TemplateView

from .models import Category
from .models import FrequentlyAskedQuestion

class FAQCategoryList(TemplateView):
    template_name = "faq-category-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.filter(published=True) \
        .all()

        return context

class CategoryQuestionView(TemplateView):
    template_name = "faq-question.html"

    def get_context_data(self, category_id, question_id, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            category = Category.objects.get(id=category_id)
            question = FrequentlyAskedQuestion.objects.get(id=question_id)
        except (Category.DoesNotExist, Question.DoesNotExist) as e:
            raise Http404('Not found') 

        context['category'] = category
        context['question'] = question
        return context