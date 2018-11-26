from django.conf.urls import patterns, include, url
from . import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'semantic.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
]
