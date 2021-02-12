import random

from django import forms
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.urls import reverse

from resources.models import Article
from faqs.models import FrequentlyAskedQuestion
from faqs.models import Category as FAQCategory
from patients.models import Patient
from patients.models import PatientStoryHighlight
from patients.views import PatientStoryList

class WebsiteConfigurationForm(forms.Form):
    show_content_on_homepage = forms.BooleanField(
        label = 'Show content on homepage',
        required = False
    )
    show_top_navigation = forms.BooleanField(
        label = 'Show top navigation',
        required = False
    )

class HomePageView(TemplateView):

    template_name = 'home-page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        show_top_navigation = self.request.session['show_top_navigation'] if 'show_top_navigation' in self.request.session else True
        show_content = self.request.session['show_content_on_homepage'] if 'show_content_on_homepage' in self.request.session else False
        survey_complete = self.request.session['survey-complete'] if 'survey-complete' in self.request.session else False
        if survey_complete:
            context['took_survey'] = True
        if show_content:
            contents = []
            for article in Article.objects.all():
                contents.append({
                    'title': article.title,
                    'excerpt': article.description,
                    'content_type': 'article',
                    'link': reverse('website-resource-article', kwargs={
                        'article_id': article.id
                    })
                })
            for question in FrequentlyAskedQuestion.objects.all():
                contents.append({
                    'title': question.text,
                    'content_type': 'question',
                    'link': reverse('website-faq', kwargs={
                        'question_id': question.id
                    })
                })
            for story_highlight in PatientStoryHighlight.objects.all():
                contents.append({
                    'title': story_highlight.patient.name,
                    'content_type': 'story',
                    'excerpt': story_highlight.content
                })
            random.shuffle(contents)
            if survey_complete:
                contents = contents[:7]
            context['contents'] = contents
            
        context['show_top_navigation'] = show_top_navigation
        context['form'] = WebsiteConfigurationForm({
            'show_top_navigation': show_top_navigation,
            'show_content_on_homepage': show_content
        })
        return context

    def post(self, request):
        form = WebsiteConfigurationForm(request.POST)
        if form.is_valid():
            for key in form.cleaned_data.keys():
                request.session[key] = form.cleaned_data[key]
            return HttpResponseRedirect(reverse('website-home'))
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)

class SearchForm(forms.Form):
    fev = forms.ChoiceField(
        label = "What is your FEV1?",
        choices = [
            (0.1, "10%"),
            (0.2, "20%"),
            (0.3, "30%"),
            (0.4, "40%"),
            (0.5, "50%"),
            (0.6, "60%"),
            (0.7, "70%"),
            (0.8, "80%"),
            (0.9, "90%"),
            ( 1, "100%")
        ],
        widget = forms.RadioSelect
    )
    age = forms.IntegerField(
        label = "How old are you?"
    )
    sex = forms.ChoiceField(
        label = "Which sex were you assigned at birth?",
        choices = [
            ("male", "Male"),
            ("female", "Female")
        ],
        widget = forms.RadioSelect
    )
    treatments = forms.MultipleChoiceField(
        label = "Are you using any of the following treatments?",
        choices = [
            (1, "Ivacaftor (Kalydeco)"),
            (2, "Elexacaftor/Tezacaftor/Ivacaftor (Trikafta)"),
            (3, "Using supplemental oxygen")
        ],
        widget = forms.CheckboxSelectMultiple
    )
    exacerbations = forms.IntegerField(
        label = "How many exacerbations have you had in the past year?"
    )

class MyCFStageSurveyView(TemplateView):
    template_name = 'patient-search-form.html'

    SURVEY_KEYS = ['fev', 'age', 'sex', 'treatments', 'exacerbations']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_session_data = {}
        for key in self.SURVEY_KEYS:
            current_session_data[key] = self.request.session[key] if key in self.request.session else None
        context['form'] = SearchForm(initial=current_session_data)
        context['survey_complete'] = self.request.session['survey-complete'] if 'survey-complete' in self.request.session else False
        return context

    def post(self, request):
        if 'reset' in request.POST:
            for key in self.SURVEY_KEYS:
                if key in request.session:
                    request.session[key] = None
            request.session['survey-complete'] = False
            return HttpResponseRedirect(reverse('website-home'))
        form = SearchForm(request.POST)
        if form.is_valid():
            for key in self.SURVEY_KEYS:
                request.session[key] = form.cleaned_data[key]
            request.session['survey-complete'] = True
            return HttpResponseRedirect(reverse('website-home'))
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)

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
