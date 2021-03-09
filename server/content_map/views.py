from bs4 import BeautifulSoup
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.base import TemplateView
import readability
import syntok.segmenter as segmenter

from website.views import BaseWebsiteView
from website.models import RelatedItemsList

from faqs.models import Answer
from faqs.models import FrequentlyAskedQuestion
from faqs.models import Category as FAQCategory
from resources.models import Article
from patients.models import Patient
from patients.models import PatientStory

class ContentMapView(BaseWebsiteView):

    content_list = []
    template_name = 'content-map.html'

    def get_patients(self):
        patients = Patient.objects.filter(
            published = True
        ).order_by('name')
        return list(patients)

    def analyze_frequently_asked_question(self, question):
        return self.analyze_html(''.join([response.text for response in question.responses]))

    def analyze_faq_response(self, response):
        return self.analyze_html(response.text)

    def analyze_patient_story(self, patient_story):
        return {
            'type': 'patient-story',
            'title': patient_story.title,
            'readability': self.analyze_html(patient_story.content),
            'content': patient_story.content
        }

    def analyze_patient(self, patient):
        full_content = [story.content for story in patient.stories]
        return self.analyze_html(''.join(full_content))

    def analyze_resource_article_content(self, article):
        return self.analyze_html(article.content)

    def analyze_resource_article(self, article):
        full_content = [article.content] + [child.content for child in article.children]
        return self.analyze_html(''.join(full_content))

    def tokenize_text(self, text):
        paragraphs = []
        for paragraph in segmenter.analyze(text):
            sentences = []
            for sentence in paragraph:
                sentences.append(' '.join([token.value for token in sentence]))
            paragraphs.append('\n'.join(sentences))
        return '\n\n'.join(paragraphs)

    def analyze_text(self, text):
        tokenized = self.tokenize_text(text)
        measures = readability.getmeasures(tokenized, lang='en')
        return {
            'grade_level': measures['readability grades']['Kincaid'],
            'words': measures['sentence info']['words'],
            'words_per_sentence': measures['sentence info']['words_per_sentence'],
            'sentences_per_paragraph': measures['sentence info']['sentences_per_paragraph'],
            'paragraphs': measures['sentence info']['paragraphs']
        }
    
    def analyze_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        return self.analyze_text('\n\n'.join([p.text for p in soup.find_all('p')]))

    def get_resource_articles(self):
        articles = Article.objects.filter(
            published = True,
            parent = None
        ).all()
        return list(articles)


    def get_frequently_asked_questions(self):
        questions = []
        for category in FAQCategory.objects.filter(published=True).all():
            questions += category.questions
        return questions

    def get_content_list(self, content_id):
        if content_id == 'stories':
            return self.get_patients()
        if content_id == 'resources':
            return self.get_resource_articles()
        if content_id == 'questions':
            return self.get_frequently_asked_questions()
        content = self.get_content_from_id(content_id)
        if content:
            if isinstance(content, Patient):
                return content.get_stories()
            if isinstance(content, Article):
                return [content] + [child for child in content.children]
            if isinstance(content, FrequentlyAskedQuestion):
                return [response for response in content.responses]
        try:
            related_list = RelatedItemsList.objects.get(name=content_id)
            return related_list.content_list
        except RelatedItemsList.DoesNotExist:
            return []

    def analyze_content(self, content):
        if isinstance(content, Article):
            return self.analyze_resource_article(content)
        if isinstance(content, Patient):
            return self.analyze_patient(content)
        if isinstance(content, FrequentlyAskedQuestion):
            return self.analyze_frequently_asked_question(content)
        if isinstance(content, Answer):
            return self.analyze_faq_response(content)
        return {
            'type': 'unknown',
            'title': 'Unknown Content'
        }

    def serialize_related_content(self, content):
        serialized = []
        for _content in self.get_related_content(content):
            serialized.append({
                'title': self.get_content_title(_content),
                'content_id': self.get_content_id(_content),
                'content_type': self.get_content_type(_content)
            })
        return serialized

    def serialize_content_list(self, content_list):
        serialized = []
        for content in content_list:
            serialized.append({
                'title': self.get_content_title(content),
                'id': content.id,
                'content_id': self.get_content_id(content),
                'content_type': self.get_content_type(content),
                'readability': self.analyze_content(content),
                'related_content': self.serialize_related_content(content)
            })
        return serialized

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.content_list:
            context['content_list'] = self.serialize_content_list(self.content_list)
        return context

    def setup(self, request, content_id=None, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if content_id is not None:
            self.content_list = self.get_content_list(content_id)
            if not self.content_list:
                raise Http404('Not found')
