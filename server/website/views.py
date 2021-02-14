import random

from django import forms
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic.base import TemplateView

from resources.models import Article
from faqs.models import FrequentlyAskedQuestion
from faqs.models import Category as FAQCategory
from patients.models import Patient
from patients.models import PatientStoryHighlight

from .models import RelatedItem
from .models import RelatedItemsList
from .models import StudySession

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

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if 'study_session_id' in request.session and request.session['study_session_id'] is not None:
            self.setup_study_session(request.session['study_session_id'])
        else:
            self.setup_session_configuration()

    def setup_study_session(self, study_session_id):
        try:
            study_session = StudySession.objects.get(id=study_session_id)
            self.study_session = study_session
            if study_session.high_agency_version:
                self.show_recommended_content = False
            else:
                self.show_recommended_content = True
            if study_session.integrated_content_version:
                self.show_top_navigation = False
                self.show_content_on_homepage = True
            else:
                self.show_top_navigation = True
                self.show_content_on_homepage = False
        except StudySession.DoesNotExist:
            self.setup_session_configuration()

    def setup_session_configuration(self):
        self.study_session = None
        self.show_recommended_content = self.request.session['show_recommended_content'] if 'show_recommended_content' in self.request.session else True
        self.show_top_navigation = self.request.session['show_top_navigation'] if 'show_top_navigation' in self.request.session else True
        self.show_content_on_homepage = self.request.session['show_content_on_homepage'] if 'show_content_on_homepage' in self.request.session else False

    def get_question_related_content(self, question):
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['study_session'] = self.study_session
        context['took_survey'] = self.request.session['survey-complete'] if 'survey-complete' in self.request.session else False
        context['show_top_navigation'] = self.show_top_navigation
        context['show_content'] = self.show_content_on_homepage
        context['form'] = WebsiteConfigurationForm({
            'show_top_navigation': context['show_top_navigation'],
            'show_content_on_homepage': context['show_content']
        })
        return context

class HomePageView(BaseWebsiteView):

    template_name = 'home-page.html'

    def render_article(self, article):
        return render_to_string('resource-article-partial.html', {
            'article': article
        })

    def render_question(self, question):
        return render_to_string('question-partial.html', {
            'question': question
        })

    def render_patient(self, patient):
        return render_to_string('patient-story-partial.html', {
            'patient': patient
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if context['show_content']:
            contents = []
            for article in Article.objects.all():
                contents.append(self.render_article(article))
            for question in FrequentlyAskedQuestion.objects.all():
                contents.append(self.render_question(question))
            for patient in Patient.objects.filter(published=True).all():
                contents.append(self.render_patient(patient))
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
            return HttpResponseRedirect(reverse('home'))
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

class StudySessionView(TemplateView):

    def post(self, request):
        if 'clear' in request.POST and request.session['study_session_id']:
            request.session['study_session_id'] = None
            return HttpResponseRedirect(reverse('home'))
        study_session = None
        if 'prototype-a' in request.POST:
            study_session = StudySession.objects.create(
                high_agency_version = True,
                integrated_content_version = False
            )
        if 'prototype-b' in request.POST:
            study_session = StudySession.objects.create(
                high_agency_version = True,
                integrated_content_version = False
            )
        if study_session:
            request.session['study_session_id'] = study_session.id
        return HttpResponseRedirect(reverse('home'))


class PatientStoryListView(BaseWebsiteView):

    template_name = 'patient-story-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patients = Patient.objects.filter(published=True).all()

        context['patients'] = patients
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

    def get_related_list(self, question):
        try:
            return RelatedItemsList.objects.get(
                name = 'question-{id}'.format(id=question.id)
            )
        except RelatedItemsList.DoesNotExist:
            return RelatedItemsList.objects.create(
                name = 'question-{id}'.format(id=question.id)
            )

    def get_related_content(self, question):
        related_list = self.get_related_list(question)
        return related_list.items

    def get_context_data(self, question_id, **kwargs):
        try:
            question = FrequentlyAskedQuestion.objects.get(id=question_id)
        except FrequentlyAskedQuestion.DoesNotExist:
            raise Http404('Question does not exist')
        context = super().get_context_data(**kwargs)
        context['question'] = question
        context['related_content'] = self.get_related_content(question)
        return context

class ReorderRelatedContent(FrequentlyAskedQuestionView):

    template_name = 'reorder-related-content.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = context['question']
        related_content = context['related_content']
        serialized_content = []
        for content in related_content:
            serialized_content.append({
                'id': 'question-%d' % (content.id),
                'text': content.text
            })
        context['related_content'] = serialized_content
        return context

    def post(self, request, question_id, **kwargs):

        try:
            question = FrequentlyAskedQuestion.objects.get(id=question_id)
        except FrequentlyAskedQuestion.DoesNotExist:
            raise Http404('Question does not exist')
        related_list = self.get_related_list(question)
        related_items = RelatedItem.objects.filter(item_list=related_list).all()
        related_by_id = {}
        for related_item in related_items:
            content_id = 'question-%d' % (related_item.object_id)
            related_by_id[content_id] = related_item
        
        ordered_content = request.POST.getlist('ordered_content[]')
        new_item_list = []
        for ordered_content_id in ordered_content:
            if ordered_content_id in related_by_id:
                new_item_list.append(related_by_id[ordered_content_id])

        for related_item in related_items:
            if related_item not in new_item_list:
                related_item.delete()

        for index, related_item in enumerate(new_item_list):
            related_item.order = (index + 1) * 10
            related_item.save()

        return HttpResponseRedirect(reverse('question', kwargs={
            'question_id': question.id
        }))

class FrequentlyAskedQuestionRelatedContentView(FrequentlyAskedQuestionView):

    template_name = 'add-related-content-page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = context['question']
        related_content = self.get_related_content(question)
        selected_questions = related_content
        all_questions = FrequentlyAskedQuestion.objects.filter(
            published = True
        ).exclude(
            id = context['question'].id
        ).all()

        context['questions'] = []
        for question in all_questions:
            selected = False
            if question.id in [q.id for q in selected_questions if q is not None]: 
                selected = True
            context['questions'].append({
                'text': question.text,
                'id': question.id,
                'selected': selected
            })

        return context

    def post(self, request, question_id, **kwargs):
        try:
            question = FrequentlyAskedQuestion.objects.get(id=question_id)
        except FrequentlyAskedQuestion.DoesNotExist:
            raise Http404('Question does not exist')
        related_list = self.get_related_list(question)
        RelatedItem.objects.filter(item_list=related_list).delete()
        if 'related_content[]' in request.POST:
            for item in request.POST.getlist('related_content[]'):
                content_type, content_id = item.split('-')
                try:
                    _question = FrequentlyAskedQuestion.objects.get(id=content_id)
                except FrequentlyAskedQuestion.DoesNotExist:
                    continue
                RelatedItem.objects.create(
                    item_list = related_list,
                    content_object = _question
                )

        
        return HttpResponseRedirect(reverse('question', kwargs={
            'question_id': question.id
        }))
