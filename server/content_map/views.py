from bs4 import BeautifulSoup
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import TemplateView
import readability

from resources.models import Article
from patients.models import Patient
from patients.models import PatientStory

class ContentMapView(TemplateView):

    content_list = []
    template_name = 'content-map.html'

    def get_patients(self):
        patients = Patient.objects.filter(
            published = True
        ).order_by('name')
        return list(patients)

    def analyze_patient_story(self, patient_story):
        soup = BeautifulSoup(patient_story.content, 'html.parser')
        content = soup.text
        return {
            'type': 'patient-story',
            'title': patient_story.title,
            'readability': self.analyze_text(content),
            'content': content
        }

    def analyze_patient(self, patient):
        return {
            'type': 'patient',
            'title': patient.name,
            'children': [self.analyze_patient_story(story) for story in patient.stories]
        }

    def analyze_resource_article_content(self, article):
        soup = BeautifulSoup(article.content, 'html.parser')
        content = soup.text
        return {
            'type': 'resource-article',
            'title': article.title,
            'readability': self.analyze_text(content),
            'content': content
        }

    def analyze_resource_article(self, article):
        return {
            'type': 'resource-article',
            'title': article.title,
            'readability': self.analyze_text(article.description),
            'children': [self.analyze_resource_article_content(child) for child in article.children]
        }

    def analyze_text(self, text):
        measures = readability.getmeasures(text)
        return {
            'grade_level': measures['readability grades']['Kincaid'],
            'words': measures['sentence info']['words'],
            'words_per_sentence': measures['sentence info']['words_per_sentence'],
            'sentences_per_paragraph': measures['sentence info']['sentences_per_paragraph'],
            'paragraphs': measures['sentence info']['paragraphs']
        }

    def get_resource_articles(self):
        articles = Article.objects.filter(
            published = True,
            parent = None
        ).all()
        return list(articles)


    def get_frequently_asked_questions(self):
        return []

    def get_content_list(self, content_id):
        if content_id == 'stories':
            return self.get_patients()
        if content_id == 'resources':
            return self.get_resource_articles()
        if content_id == 'questions':
            return self.get_frequently_asked_questions()
        return []

    def analyze_content(self, content):
        if isinstance(content, Article):
            return self.analyze_resource_article(content)
        if isinstance(content, Patient):
            return self.analyze_patient(content)
        return {
            'type': 'unknown',
            'title': 'Unknown Content'
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.content_list:
            context['content_list'] = [self.analyze_content(content) for content in self.content_list]
        return context

    def setup(self, request, content_id=None, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if content_id is not None:
            self.content_list = self.get_content_list(content_id)
            if not self.content_list:
                raise Http404('Not found')
