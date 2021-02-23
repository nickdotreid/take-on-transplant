import random

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
from patients.models import PatientStory
from patients.models import PatientStoryHighlight
from patients.views import PatientStoryView as OGPatientStoryView

from .forms import WebsiteConfigurationForm
from .forms import MyCFStageForm
from .models import RelatedItem
from .models import RelatedItemsList
from .models import StudySession



class BaseWebsiteView(TemplateView):

    study_session = None

    show_top_navigation = True
    show_recommended_content = True
    show_content_on_homepage = False
    show_survey = False
    survey_complete = False

    FEATURE_FLAGS = [
        'show_recommended_content',
        'show_top_navigation',
        'show_content_on_homepage',
        'show_survey',
        'survey_complete'        
    ]

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
                self.show_survey = False
            else:
                self.show_recommended_content = True
                self.show_survey = True
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
        for flag in self.FEATURE_FLAGS:
            if flag in self.request.session:
                setattr(self, flag, self.request.session[flag])

    def get_related_list(self, question):
        try:
            return RelatedItemsList.objects.get(
                name = 'question-{id}'.format(id=question.id)
            )
        except RelatedItemsList.DoesNotExist:
            return RelatedItemsList.objects.create(
                name = 'question-{id}'.format(id=question.id)
            )

    def get_related_items(self, question):
        related_list = self.get_related_list(question)
        return related_list.items

    def get_related_content(self, question):
        related_list = self.get_related_list(question)
        return related_list.content_list

    def render_related_content(self, content):
        related_list = self.get_related_list(content)
        rendered_content = []
        for _content in related_list.content_list:
            rendered = self.render_content(_content)
            if rendered:
                rendered_content.append(rendered)
        return rendered_content

    def render_content(self, content):
        if isinstance(content, FrequentlyAskedQuestion):
            return self.render_question(content)
        if isinstance(content, Patient):
            return self.render_patient(content)
        if isinstance(content, Article):
            return self.render_article(content)
        return None

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

    def get_and_render_all_content(self):
        contents = []
        for article in Article.objects.filter(published=True, parent=None).all():
            contents.append(self.render_article(article))
        for question in FrequentlyAskedQuestion.objects.filter(published=True).all():
            contents.append(self.render_question(question))
        for patient in Patient.objects.filter(published=True).all():
            contents.append(self.render_patient(patient))
        random.shuffle(contents)
        return contents

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['study_session'] = self.study_session
        context['took_survey'] = self.request.session['survey-complete'] if 'survey-complete' in self.request.session else False
        
        context['show_top_navigation'] = self.show_top_navigation
        context['show_content'] = self.show_content_on_homepage
        context['show_survey'] = self.show_survey
        context['show_recommended_content'] = self.show_recommended_content
        
        return context

class HomePageView(BaseWebsiteView):

    template_name = 'home-page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['home_form'] = WebsiteConfigurationForm({
            'features': [feature for feature, label in WebsiteConfigurationForm.FEATURE_FLAGS if feature in self.request.session and self.request.session[feature]]
        })

        if context['show_content'] and context['took_survey']:
            patients = []
            try:
                will = Patient.objects.get(name='Will')
                context['will'] = will
                patients.append(will)
            except Patient.DoesNotExist():
                pass
            try:
                amy = Patient.objects.get(name='Amy')
                context['amy'] = amy
                patients.append(amy)
            except Patient.DoesNotExist():
                pass

            context['patients'] = Patient.objects.filter(name__in=['Amy', 'Will']).order_by('-name').all()

            questions = FrequentlyAskedQuestion.objects.filter(id__in=[1,5]).all()
            context['questions'] = questions

            resources = Article.objects.filter(id__in=[14, 9]).order_by('title').all()
            context['resources'] = resources
            
            contents = [p for p in patients]
            contents += resources
            contents += questions
            context['contents'] = [self.render_content(c) for c in contents]
        return context

    def post(self, request):
        form = WebsiteConfigurationForm(request.POST)
        if form.is_valid():
            for flag, label in WebsiteConfigurationForm.FEATURE_FLAGS:
                request.session[flag] = None
            for key in form.cleaned_data['features']:
                request.session[key] = True
            return HttpResponseRedirect(reverse('home'))
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)

class ContentListView(BaseWebsiteView):

    template_name = 'content-list-page'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class AllContentView(BaseWebsiteView):

    template_name = 'all-content-page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contents'] = self.get_and_render_all_content()
        return context

class MyCFStageSurveyView(BaseWebsiteView):
    template_name = 'patient-search-form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_session_data = {}
        context['form'] = MyCFStageForm(initial=current_session_data)
        context['survey_complete'] = self.request.session['survey-complete'] if 'survey-complete' in self.request.session else False
        return context

    def post(self, request):
        if 'reset' in request.POST:
            request.session['survey-complete'] = False
            return HttpResponseRedirect(reverse('home'))
        form = MyCFStageForm(request.POST)
        if form.is_valid():
            request.session['survey-complete'] = True
            return HttpResponseRedirect(reverse('home'))
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)

class StudySessionView(TemplateView):

    def post(self, request):
        if 'clear' in request.POST and request.session['study_session_id']:
            request.session['study_session_id'] = None
            return HttpResponseRedirect(reverse('home'))
        study_session = None
        if 'marco' in request.POST:
            study_session = StudySession.objects.create(
                persona = 'marco',
                high_agency_version = True,
                integrated_content_version = False
            )
        if 'tamika' in request.POST:
            study_session = StudySession.objects.create(
                persona = 'tamika',
                high_agency_version = False,
                integrated_content_version = True
            )
        if study_session:
            request.session['study_session_id'] = study_session.id
        return HttpResponseRedirect(reverse('home'))


class PatientStoryListView(ContentListView):

    template_name = 'patient-story-list-page.html'

    def get_sort_options(self):
        return [
            ('alphabetical', 'Alphabetical'),
            ('age', 'Age'),
            ('fev1before', 'Fev1 Before Transplant'),
            ('current-fev1', 'Current Fev1')
        ]
    
    def get_sort_order_and_name(self):
        sort_options = self.get_sort_options()
        sort_order = sort_options[0][0]
        sort_name = sort_options[0][1]
        if 'sort' in self.request.GET:
            for key, name in sort_options:
                if key == self.request.GET['sort']:
                    sort_order = key
                    sort_name = name
        return (sort_order, sort_name)

    def sort_patients(self, patients, sort_order):
        if sort_order == 'alphabetical':
            patients.sort(key=lambda p: p.name)
        if sort_order == 'age':
            patients.sort(
                key=lambda p: p.get_value(['age', 'age-at-transplant']) if p.get_value(['age', 'age-at-transplant']) else 0,
                reverse=True
            )
        if sort_order == 'fev1before':
            value_keys = ['fev1-at-transplant', 'fev1-at-transplant-evaluation']
            patients.sort(
                key=lambda p: p.get_value(value_keys) if p.get_value(value_keys) else 0,
                reverse=True
            )
        if sort_order == 'current-fev1':
            value_keys = ['current-fev1']
            patients.sort(
                key=lambda p: p.get_value(value_keys) if p.get_value(value_keys) else 0,
                reverse=True
            )
        return patients

    def serialize_sort_options(self, selected_sort_order=None):
        sort_options = self.get_sort_options()
        serialized_options = []
        for key, name in sort_options:
            selected = False
            if key == selected_sort_order:
                selected = True
            serialized_options.append({
                'name': name,
                'selected': selected,
                'value': key
            })
        return serialized_options

    def get_filters_for_patients(self, patients):
        filters = [{
            'title': 'Gender',
            'slug': 'gender',
            'keys': ['gender']
        }, {
            'title': 'Genotype',
            'slug': 'genotype',
            'keys': ['cftr genotype']
        }, {
            'title': 'Modulator Status',
            'slug': 'modulator-status',
            'keys': ['CFTR modulator status at transplant']
        }]
        for patient in patients:
            for _filter in filters:
                value, slug = patient.get_value_pairs(_filter['keys'])
                if value is not None:
                    if 'options' not in _filter:
                        _filter['options'] = {}
                    if slug not in _filter['options']:
                        _filter['options'][slug] = {
                            'name': value,
                            'slug': slug,
                            'count': 0
                        }
                    _filter['options'][slug]['count'] += 1
        return filters

    def filter_patients(self, filters, patients):
        for _filter in filters:
            if _filter['slug'] in self.request.GET:
                value = self.request.GET[_filter['slug']]
                if value != '':
                    patients = [p for p in patients if p.get_value_pairs(_filter['keys'])[1] == value]
        return patients      

    def serialize_filters(self, filters):
        serialized_filters = []
        for _filter in filters:
            options_flattened = list(_filter['options'].values())
            options_flattened.sort(key=lambda x: x['name'])
            has_selected_option = False
            for option in options_flattened:
                if _filter['slug'] in self.request.GET:
                    if option['slug'] == self.request.GET[_filter['slug']]:
                        option['selected'] = True
                        has_selected_option = True
            options_flattened.append({
                'name': 'Show All',
                'slug': '',
                'selected': not has_selected_option
            })
            serialized_filters.append({
                'title': _filter['title'],
                'slug': _filter['slug'],
                'options': options_flattened
            })
        return serialized_filters


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patients = list(Patient.objects.filter(published=True).all())
        
        sort_order, sort_name = self.get_sort_order_and_name()
        patients = self.sort_patients(patients, sort_order)

        context['number_patients'] = len(patients)

        filters = self.get_filters_for_patients(patients)
        patients = self.filter_patients(filters, patients)
        context['filters'] = self.serialize_filters(filters)

        context['number_patients_showing'] = len(patients)
        
        context['content_list'] = [self.render_patient(p) for p in patients]

        context['sort_order'] = sort_order
        context['sort_name'] = sort_name
        context['sort_options'] = self.serialize_sort_options(sort_order)

        return context

class ContentPageView(BaseWebsiteView):

    template_name = 'content-page.html'

class PatientStoryView(ContentPageView):

    def render_patient_story(self, patient_story):
        return render_to_string('story-partial.html', {
            'id': patient_story.id,
            'title': patient_story.title,
            'content': patient_story.content
        })

    def get_context_data(self, patient_id, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            raise Http404('Patient not found')

        patient_story_sections = patient.get_stories()

        context['nav_items'] = []
        for story in patient_story_sections:
            context['nav_items'].append({
                'name': story.title,
                'id': 'story-%d' % (story.id)
            })
        
        context['content_type'] = 'patient'
        context['content_id'] = patient.id
        context['title'] = patient.name
        context['content_items'] = [self.render_patient_story(story) for story in patient_story_sections]
        context['related_content'] = self.render_related_content(patient)
        return context

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

class ResourceArticleView(ContentPageView):

    def render_article_page(self, article):
        return render_to_string('resource-article.html', {
            'article': article
        })

    def get_context_data(self, article_id, **kwargs):
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            raise Http404('No Article')
        context = super().get_context_data(**kwargs)

        context['nav_items'] = [{
            'name': article.title,
            'id': 'article-%d' % (article.id)
        }]
        for _article in article.children:
            context['nav_items'].append({
                'name': _article.title,
                'id': 'article-%d' % (_article.id)
            })
        
        context['content_type'] = 'resource'
        context['content_id'] = article.id
        context['title'] = article.title
        context['content_items'] = [self.render_article_page(article)]

        return context

class FrequentlyAskedQuestionListView(BaseWebsiteView):

    template_name = 'frequently-asked-question-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = FAQCategory.objects.all()
        return context

class FrequentlyAskedQuestionView(ContentPageView):

    def render_faq_response(self, response):
        return render_to_string('faq-response.html',{
            'response': response
        })

    def get_context_data(self, question_id, **kwargs):
        try:
            question = FrequentlyAskedQuestion.objects.get(id=question_id)
        except FrequentlyAskedQuestion.DoesNotExist:
            raise Http404('Question does not exist')
        context = super().get_context_data(**kwargs)
        context['content_type'] = 'question'
        context['content_id'] = question.id
        context['title'] = question.text
        context['nav_items'] = [{'id':'top', 'name':question.text}] + [{'id': 'response-%d' % (response.id), 'name':response.author.name if response.author else None } for response in question.responses]
        context['content_items'] = ['<h1 id="top">%s</h1>' % (question.text)] + [self.render_faq_response(response) for response in question.responses]
        context['related_content'] = self.render_related_content(question)
        return context

class RelatedContentView(BaseWebsiteView):

    template_name = 'add-related-content-page.html'

    CONTENT_TYPES = {
        'patient': Patient,
        'question': FrequentlyAskedQuestion,
        'resource': Article
    }

    def get_question(self, question_id):
        try:
            return FrequentlyAskedQuestion.objects.get(id=question_id)
        except FrequentlyAskedQuestion.DoesNotExist:
            raise Http404('Question does not exist')

    def get_content(self, content_type, content_id):
        for key, _model in self.CONTENT_TYPES.items():
            if content_type == key:
                try:
                    return _model.objects.get(id=content_id)
                except _model.DoesNotExist:
                    raise Http404('Content not found')
        raise Http404('Unknown content type')

    def get_all_questions(self, questions_to_exclude):
        return FrequentlyAskedQuestion.objects.filter(
            published = True
        ).exclude(
            id__in = [q.id for q in questions_to_exclude]
        ).all()

    def serialize_question(self, question):
        return {
            'title': question.text,
            'content_id': self.get_content_id(question)
        }

    def serialize_patient(self, patient):
        return {
            'title': patient.name,
            'content_id': self.get_content_id(patient)
        }

    def serialize_resource(self, resource):
        return {
                'title': resource.title,
                'content_id': self.get_content_id(resource)
        }

    def serialize_questions(self, questions):
        serialized = []
        for question in questions:
            serialized.append(self.serialize_question(question))
        return serialized

    def serialize_patients(self, patients):
        serialized = []
        for patient in patients:
            serialized.append(self.serialize_patient(patient))
        return serialized

    def serialize_resources(self, resources):
        serialized = []
        for resource in resources:
            serialized.append(self.serialize_resource(resource))
        return serialized
    
    def serialize_content(self, content_object):
        for key, model in self.CONTENT_TYPES.items():
            if isinstance(content_object, model):
                if key == 'question':
                    return self.serialize_question(content_object)
                if key == 'patient':
                    return self.serialize_patient(content_object)
                if key == 'resource':
                    return self.serialize_resource(content_object)

    def get_content_id(self, content_object):
        for key, model in self.CONTENT_TYPES.items():
            if isinstance(content_object, model):
                return '{key}-{id}'.format(
                    key=key,
                    id = content_object.id
                )
        return None
    
    def get_content_from_id(self, content_id):
        content_type, content_id = content_id.split('-')
        if content_type in self.CONTENT_TYPES:
            _model = self.CONTENT_TYPES[content_type]
            try:
                return _model.objects.get(id=content_id)
            except _model.DoesNotExist:
                pass
        return None

    def get_content_url(self, content_object):
        for key, model in self.CONTENT_TYPES.items():
            if isinstance(content_object, model):
                if key == 'question':
                    return reverse('question', kwargs={
                        'question_id': content_object.id
                    })
                if key == 'resource':
                    return reverse('resource-article', kwargs={
                        'article_id': content_object.id
                    })
                if key == 'patient':
                    return reverse('patient-story', kwargs={
                        'patient_id': content_object.id
                    })
        return None

    def get_context_data(self, content_type, content_id, **kwargs):
        context = super().get_context_data(**kwargs)
        self.content_object = self.get_content(content_type, content_id)
        
        self.related_content = self.get_related_items(self.content_object)
        context['related_content'] = [self.get_content_id(rc.content_object) for rc in self.related_content]

        all_questions = FrequentlyAskedQuestion.objects.filter(published=True).all()
        all_patients = Patient.objects.filter(
            published = True
        ).all()
        all_resources = Article.objects.filter(
            published = True,
            parent = None
        ).all()
        context['content_types'] = [
            {
                'title': 'Questions',
                'items': self.serialize_questions(all_questions)
            },
            {
                'title': 'Patient Stories',
                'items': self.serialize_patients(all_patients)
            },
            {
                'title': 'Resource Articles',
                'items': self.serialize_resources(all_resources)
            }
        ]

        return context

    def post(self, request, content_type, content_id, **kwargs):
        content = self.get_content(content_type, content_id)
        related_list = self.get_related_list(content)
        RelatedItem.objects.filter(item_list=related_list).delete()
        if 'related_content[]' in request.POST:
            for item in request.POST.getlist('related_content[]'):
                content_object = self.get_content_from_id(item)
                if content_object:
                    RelatedItem.objects.create(
                        item_list = related_list,
                        content_object = content_object
                    )
        return HttpResponseRedirect(self.get_content_url(content))

class ReorderRelatedContent(RelatedContentView):

    template_name = 'reorder-related-content.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        related_content = self.related_content
        serialized_content = []
        for item in related_content:
            serialized_content.append(self.serialize_content(item.content_object))
        context['related_content'] = serialized_content
        return context

    def post(self, request, content_type, content_id, **kwargs):
        content = self.get_content(content_type, content_id)
        related_list = self.get_related_list(content)
        related_items = RelatedItem.objects.filter(item_list=related_list).all()
        related_by_id = {}
        for related_item in related_items:
            content_id = self.get_content_id(related_item.content_object)
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

        return HttpResponseRedirect(self.get_content_url(content))
