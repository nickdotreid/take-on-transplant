import json
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.views import View

from study_sessions.models import StudySession

from .models import Highlight
from .models import HighlightedContent

class HighlightsView(View):

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
