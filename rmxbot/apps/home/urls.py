
from django.urls import path

from rmxbot.apps.home import views


urlpatterns = [

    path('', views.home),
    path('see-how-it-works', views.HowTo.as_view(), name='howto'),

]
