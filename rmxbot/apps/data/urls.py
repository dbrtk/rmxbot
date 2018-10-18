

from django.conf.urls import url
from django.urls import path
from rmxbot.apps.data import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'thesite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    # url(r'^$', 'rmxbot.apps.data.views.get_data'),

    url(r'^$', views.index),

    url(r'^create/$', views.create),
    url(r'^create-data-object/', views.create),

    url(r'^data-to-corpus/$', views.data_to_corpus),
    path('edit-many/', views.edit_many),

    url(r'^webpage/(?P<docid>[0-9a-zA-Z]*)/$', views.webpage),

    url(r'^text/(?P<docid>[0-9a-zA-Z]*)/$', views.text),
]
