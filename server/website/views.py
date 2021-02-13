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

class BaseWebsiteView(TemplateView):
    
    def get_patient_story_link(self, patient):
        return reverse('patient-story', kwargs={
            'patient_id': patient.id
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_top_navigation'] = self.request.session['show_top_navigation'] if 'show_top_navigation' in self.request.session else True
        context['show_content'] = self.request.session['show_content_on_homepage'] if 'show_content_on_homepage' in self.request.session else False
        context['took_survey'] = self.request.session['survey-complete'] if 'survey-complete' in self.request.session else False
        
        context['form'] = WebsiteConfigurationForm({
            'show_top_navigation': context['show_top_navigation'],
            'show_content_on_homepage': context['show_content']
        })
        return context

class HomePageView(BaseWebsiteView):

    template_name = 'home-page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if context['show_content']:
            contents = []
            for article in Article.objects.all():
                contents.append({
                    'object': article,
                    'title': article.title,
                    'excerpt': article.description,
                    'content_type': 'article',
                    'link': reverse('website-resource-article', kwargs={
                        'article_id': article.id
                    })
                })
            for question in FrequentlyAskedQuestion.objects.all():
                contents.append({
                    'object': question,
                    'title': question.text,
                    'content_type': 'question',
                    'link': reverse('website-faq', kwargs={
                        'question_id': question.id
                    })
                })
            for patient in Patient.objects.filter(published=True).all():
                contents.append({
                    'object': patient,
                    'title': patient.name,
                    'content_type': 'story',
                    'excerpt': patient.story_highlights[0].content if patient.story_highlights else None,
                    'link': self.get_patient_story_link(patient)
                })
            random.shuffle(contents)
            if context['took_survey']:
                contents = contents[:7]
            context['contents'] = contents
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

class MyCFStageSurveyView(BaseWebsiteView):
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

class PatientStoryListView(BaseWebsiteView):

    template_name = 'patient-story-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patients'] = Patient.objects.filter(published=True)
        return context

class PatientStoryView(BaseWebsiteView):

    template_name = 'patient-story.html'


class ResourceLibraryView(BaseWebsiteView):

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

class ResourceArticleView(BaseWebsiteView):

    template_name = 'resource-article.html'

    def get_context_data(self, article_id, **kwargs):
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            raise Http404('No Article')
        context = super().get_context_data(**kwargs)

        context['article'] = article

        return context

class FrequentlyAskedQuestionListView(BaseWebsiteView):

    template_name = 'frequently-asked-question-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = FAQCategory.objects.all()
        return context

class FrequentlyAskedQuestionView(BaseWebsiteView):

    template_name = 'frequently-asked-question.html'

    def get_context_data(self, question_id, **kwargs):
        try:
            question = FrequentlyAskedQuestion.objects.get(id=question_id)
        except FrequentlyAskedQuestion.DoesNotExist:
            raise Http404('Question does not exist')
        context = super().get_context_data(**kwargs)
        context['question'] = question
        return context
