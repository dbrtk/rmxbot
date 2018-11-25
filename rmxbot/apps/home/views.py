

from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.template import loader


def home(request):
    """
    """
    context = dict(success=True)
    template = loader.get_template("index.html")
    return HttpResponse(template.render(context, request))


class HowTo(TemplateView):

    template_name = 'about/howto.html'
