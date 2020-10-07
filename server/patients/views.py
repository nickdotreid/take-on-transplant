import logging
import re

from bs4 import BeautifulSoup
from django.http import Http404
from django.views.generic.base import TemplateView

from resources.models import Resource

from .models import Patient
from .models import PatientProperty
from .models import PatientStory

logger = logging.getLogger(__name__)

class PatientStoryList(TemplateView):

    template_name = "patient-story-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        patients = Patient.objects.order_by('name') \
        .filter(published = True) \
        .all()

        patient_properties = PatientProperty.objects.filter(
            patient_id__in = [patient.id for patient in patients],
            published = True
        ) \
        .order_by('order') \
        .prefetch_related('property') \
        .all()

        properties_by_patient_id = {}
        for patient_property in patient_properties:
            patient_id = patient_property.patient_id
            if patient_id not in properties_by_patient_id:
                properties_by_patient_id[patient_id] = []
            properties_by_patient_id[patient_id].append({
                'name': patient_property.property.name,
                'value': patient_property.value
            })

        patient_stories = PatientStory.objects.filter(
            patient_id__in = [_p.id for _p in patients],
            published = True
        ) \
        .order_by('order') \
        .all()

        story_excerpts_by_patient_id = {}
        for _story in patient_stories:
            if _story.patient_id not in story_excerpts_by_patient_id:
                story_excerpts_by_patient_id[_story.patient_id] = []
            if _story.excerpt:
                story_excerpts_by_patient_id[_story.patient_id].append({
                    'id': _story.id,
                    'excerpt': _story.excerpt,
                    'title': _story.title
                })

        serialized_patients = []
        for patient in patients:
            properties = []
            if patient.id in properties_by_patient_id:
                properties = properties_by_patient_id[patient.id]
            story_excerpts = []
            if patient.id in story_excerpts_by_patient_id:
                story_excerpts = story_excerpts_by_patient_id[patient.id]
            photo_url = None
            if patient.thumbnail:
                photo_url = patient.thumbnail.url
            serialized_patients.append({
                'id': patient.id,
                'photo_url': photo_url,
                'properties': properties,
                'name': patient.name,
                'story_excerpts': story_excerpts,
                'tags': patient.tags.filter(published=True)
            })
        context['patients'] = serialized_patients
        return context

class PatientStoryView(TemplateView):

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
                        link['data-tobble'] = resource_slug
                        resource = Resource.objects.filter(slug = resource_slug).first()
                    if resource:
                        link['data-toggle'] = "popover"
                        link['data-content'] = resource.description
            return str(soup)
        else:
            return content
    
    def get_context_data(self, patient_id, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_patient(patient_id)
        context['patient'] = {
            'id': patient.id,
            'name': patient.name
        }
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
