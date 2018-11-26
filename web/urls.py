from django.conf.urls import patterns, include, url
from .views import login, logout
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'semantic.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',login),
    url(r'^login$',login),
    url(r'^logout$',logout),
    url(r'^usermanage/',include('usermanage.urls')),
    url(r'^actionlog/',include('actionlog.urls')),
    url(r'^data/',include('datamanage.urls')),
]
