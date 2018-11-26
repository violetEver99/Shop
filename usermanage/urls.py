from django.conf.urls import patterns, include, url
from . import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'semantic.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.usermanage),
    url(r'^user$', views.userManage),
    url(r'^group$', views.groupManage),
    url(r'^perms$', views.permsManage),
    
    url(r'^getmenu$', views.getmenu),
    url(r'^changepw$', views.changepw),
    #url(r'^log$', views.logView),
]
