from django.http import Http404
from django.views.generic.base import TemplateView

from resources.models import Article
from faqs.models import FrequentlyAskedQuestion
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
