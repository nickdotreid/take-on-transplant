import json
from django.http import HttpResponse
from django.http import JsonResponse
from django.views import View

class HighlightsView(View):

    def get(self, request):
        return HttpResponse('Hi')

    def post(self, request):
        return JsonResponse({})
