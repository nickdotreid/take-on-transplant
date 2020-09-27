from django.http import Http404
from django.views.generic.base import TemplateView

from .models import Patient
from .models import PatientStory

class PatientStoryList(TemplateView):

    template_name = "patient-story-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        patients = []
        patients_query = Patient.objects.order_by('name') \
        .filter(published = True)
        for patient in patients_query.all():
            patients.append({
                'id': patient.id,
                'name': patient.name
            })
        context['patients'] = patients
        return context

class PatientStoryView(TemplateView):

    template_name = 'patient-story.html'

    def get_patient(self, patient_id):
        try:
            return Patient.objects.get(id = patient_id)
        except Patient.DoesNotExist:
            raise Http404('Patient does not exist')
    
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
                'content': story.content
            })
        context['stories'] = stories
        return context
