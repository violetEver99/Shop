from django.conf.urls import patterns, url 
from .views import *
from django.conf import settings


urlpatterns = [
    url(r'^$',actionlog),
    url(r'^log$', logManage)
]