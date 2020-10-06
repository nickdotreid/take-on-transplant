from django.http import Http404
from django.views.generic.base import TemplateView

from .models import Resource

class ResourceListView(TemplateView):

    template_name = 'resource-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        serialized_resources = []
        for _resource in Resource.objects.filter(published=True).all():
            serialized_resources.append({
                'description': _resource.description,
                'name': _resource.name,
                'slug': _resource.slug
            })
        context['resources'] = serialized_resources
        return context

class ResourceDetailView(TemplateView):

    template_name = 'resource-detail.html'

    def get_resource(self, resource_slug):
        resource = Resource.objects.filter(slug=resource_slug).first()
        if resource:
            return resource
        else:
            raise Http404('Resource does not exist')
    
    def get_context_data(self, resource_slug, **kwargs):
        context = super().get_context_data(**kwargs)
        resource = self.get_resource(resource_slug)
        context['name'] = resource.name
        context['description'] = resource.description
        context['content'] = resource.content
        return context
        
