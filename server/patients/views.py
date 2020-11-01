import logging
import re

from bs4 import BeautifulSoup
from django.http import Http404
from django.views.generic.base import TemplateView

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
