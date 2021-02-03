from django.http import Http404
from django.views.generic.base import TemplateView

from resources.models import Article
from faqs.models import FrequentlyAskedQuestion
from faqs.models import Category as FAQCategory
from patients.models import Patient
from patients.views import PatientStoryList

class HomePageView(TemplateView):

    template_name = 'home-page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class WebsitePatientStoriesView(PatientStoryList):

    template_name = 'website-patient-stories.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class ResourceLibraryView(TemplateView):

    template_name = 'resource-library.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['articles'] = Article.objects.filter(
            parent=None,
            published = True
        ) \
        .order_by('order') \
        .all()

        return context

class ResourceArticleView(TemplateView):

    template_name = 'resource-article.html'

    def get_context_data(self, article_id, **kwargs):
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            raise Http404('No Article')
        context = super().get_context_data(**kwargs)

        context['article'] = article

        return context

class FrequentlyAskedQuestionListView(TemplateView):

    template_name = 'frequently-asked-question-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = FAQCategory.objects.all()
        return context

class FrequentlyAskedQuestionView(TemplateView):

    template_name = 'frequently-asked-question.html'

    def get_context_data(self, question_id, **kwargs):
        try:
            question = FrequentlyAskedQuestion.objects.get(id=question_id)
        except FrequentlyAskedQuestion.DoesNotExist:
            raise Http404('Question does not exist')
        context = super().get_context_data(**kwargs)
        context['question'] = question
        return context
