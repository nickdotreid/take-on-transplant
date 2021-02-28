import json
from django import forms
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.views import View

from study_sessions.models import StudySession
from website.views import BaseWebsiteView

from .models import Highlight
from .models import HighlightedContent

class HighlightForm(forms.Form):
    text = forms.CharField()
    content = forms.CharField()

class HighlightsView(BaseWebsiteView):

    def get(self, request):
        return HttpResponse('Hi')

    def post(self, request):
        if 'study_session_id' not in request.session is request.session['study_session_id'] is None:
            return HttpResponseBadRequest('No session id')
        try:
            study_session = StudySession.objects.get(
                id=request.session['study_session_id']
            )
        except StudySession.DoesNotExist:
            return HttpResponseBadRequest('Study session not found') 
        highlight = Highlight.objects.create(
            session = study_session
        )
        return HttpResponse(json.dumps({
            'id': highlight.id
        }), content_type='application/json')

class HighlightDetailsView(BaseWebsiteView):

    def get_highlight(self, highlight_id):
        try:
            return Highlight.objects.get(id=highlight_id)
        except Highlight.DoesNotExist:
            raise Http404('Highlight does not exist')

    def get(self, request, highlight_id):
        highlight = self.get_highlight(highlight_id)
        return HttpResponse(json.dumps({
            'id': highlight.id,
            'text': highlight.text
        }), content_type='application/json')

    def post(self, request, highlight_id, *args, **kwargs):
        highlight = self.get_highlight(highlight_id)
        if request.is_ajax:
            post_data = json.loads(request.body)
            highlight_form = HighlightForm(post_data)
            if highlight_form.is_valid():
                print(highlight_form.cleaned_data)
                # highlight.text = highlight_form.cleaned_data['text']
                highlight.save()
                return HttpResponse(json.dumps({
                    'id': highlight.id,
                    'text': highlight.text
                }), content_type='application/json')
            else:
                return HttpResponseBadRequest('Errors in form')        
        return HttpResponseBadRequest('Bad form')
