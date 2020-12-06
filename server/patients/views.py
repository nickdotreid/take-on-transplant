import logging
import re

from bs4 import BeautifulSoup
from django.http import Http404
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

        context['patients'] = Patient.objects.order_by('name') \
        .filter(published = True) \
        .all()
        
        return context

class PatientView(TemplateView):
    resources = []
    template_name = 'patient-story.html'

    def get_patient(self, patient_id):
        try:
            return Patient.objects.get(id = patient_id)
        except Patient.DoesNotExist:
            raise Http404('Patient does not exist')

    def get_resrouces(self):
        return self.resources

    def add_resource(self, new_resource):
        if new_resource.id not in [_r.id for _r in self.resources]:
            self.resources.append(new_resource)

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
                        link['resource-id'] = resource.id
                        self.add_resource(resource)
                    definition = None
                    for slug in re.findall('.*definitions\/(.*)$', href):
                        definition = Definition.objects.filter(slug = slug).first()
                    if definition:
                        link['data-toggle'] = "popover"
                        link['data-content'] = definition.description
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
        context['resources'] = self.resources
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
