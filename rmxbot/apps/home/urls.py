from django.conf.urls import include, url

from rmxbot.apps.home import views


urlpatterns = [
    # Examples:
    # url(r'^$', 'thesite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.home),

]
