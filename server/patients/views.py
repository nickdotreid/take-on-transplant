import logging
import re
import random

from bs4 import BeautifulSoup
from django import forms
from django.http import Http404
from django.shortcuts import render
from django.views.generic.base import TemplateView

from resources.models import Definition
from resources.models import Resource

from .models import Patient
from .models import PatientAttribute
from .models import PatientStory
from .models import PatientStoryHighlight

logger = logging.getLogger(__name__)

class PatientStoryList(TemplateView):

    template_name = "patient-story-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        patients = Patient.objects.order_by('name') \
        .filter(published = True) \
        .all()

        if 'attributes' in self.request.GET:
            context['show_all_attributes'] = True
            for patient in patients:
                patient._attributes = patient.get_all_patient_attributes()

        context['patients'] = patients

        if 'highlights' in self.request.GET:
            context['show_highlights'] = True
        if 'tags' in self.request.GET:
            context['show_tags'] = True

        if 'warnings' in self.request.GET:
            context['show_warnings'] = True

        resource_ids = []
        for patient in patients:
            for patient_attribute in patient.attributes:
                attribute = patient_attribute.attribute
                if attribute.resource_id and attribute.resource_id not in resource_ids:
                    resource_ids.append(attribute.resource_id)
        context['resources'] = Resource.objects.filter(id__in=resource_ids).all()
        
        return context

class PatientView(TemplateView):
    template_name = 'patient-story.html'

    def get_patient(self, patient_id):
        try:
            return Patient.objects.get(id = patient_id)
        except Patient.DoesNotExist:
            raise Http404('Patient does not exist')

    def add_resource_popovers(self, content):
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    resource = None
                    for resource_slug in re.findall('.*resources\/(.*)$', href):
                        resource = Resource.objects.filter(slug = resource_slug).first()
                    if resource:
                        link['data-toggle'] = "popover"
                        link['class'] = "popover-highlight"
                        link['data-content'] = resource.content
            return str(soup)
        else:
            return content


class PatientStoryView(PatientView):

    template_name = 'patient-story.html'
    
    def get_context_data(self, patient_id, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_patient(patient_id)
        context['patient'] = patient
        stories = []
        story_query = PatientStory.objects.filter(patient = patient)
        for story in story_query.all():
            stories.append({
                'id': story.id,
                'title': story.title,
                'content': self.add_resource_popovers(story.content)
            })
        context['stories'] = stories
        return context

class PatientStoryTableOfContentsView(PatientView):

    template_name = 'patient-story-table-of-contents.html'

    def get_story(self, patient_id, story_id):
        try:
            return PatientStory.objects.get(
                patient_id = patient_id,
                id = story_id                
            )
        except PatientStory.DoesNotExist:
            raise Http404('No story found')

    def get_first_story(self, patient_id):
        story = PatientStory.objects.filter(
            patient_id = patient_id
        ).first()
        if story:
            return story
        else:
            raise Http404('No story found')

    def get_context_data(self, patient_id, story_id=None, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_patient(patient_id)
        context['patient'] = patient
        if story_id:
            story = self.get_story(patient_id, story_id)
        else:
            story = self.get_first_story(patient_id)
        context['stories'] = patient.stories
        context['story'] = {
            'id': story.id,
            'title': story.title,
            'content': self.add_resource_popovers(story.content)
        }
        return context

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

class PatientSearchForm(TemplateView):
    template_name = 'patient-search-form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm()
        return context

    def post(self, request):
        form = SearchForm(request.POST)
        
        context = self.get_context_data()
        context['form'] = form

        patients = Patient.objects.all()
        context['patient'] = random.choice(patients)
        context['explination'] = 'Randomly selected patient'

        return render(request, self.template_name, context)
