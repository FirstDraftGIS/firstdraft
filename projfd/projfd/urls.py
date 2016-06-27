from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.auth.models import User, Group
from django.contrib.gis import admin
from appfd import views
from django.conf import settings
import appfd, inspect

#initialize urlpatterns
urlpatterns = []

# add most urls
urlpatterns += [
    #url(r'^appfd/', include('appfd.urls')),
    #url(r'^api/', include('apifd.urls')),
    url(r'^$', views.index, name="index"),
    #url(r'about$', views.about, name='about'),
    #url(r'activate/(?P<key>[^\./]+)$', views.activate, name='activate'),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'change_email$', views.change_email, name='change_email'),
    #url(r'change_password$', views.change_password, name='change_password'),
    url(r'^contact$', views.contact, name='contact'),
    url(r'^does_map_exist/(?P<job>[^/]+)/(?P<extension>[^/]+)$', views.does_map_exist, name='does_map_exist'),
    url(r'^disclaimers$', views.disclaimers, name='disclaimers'),
    #url(r'login/$', views.login, name='login'),
    #url(r'logout/', views.user_logout, name='logout'),
    url(r"^iframe$", views.iframe, name="iframe"),
    url(r'^get_map/(?P<job>[^/]+)/(?P<extension>[^/]+)$', views.get_map, name='get_map'),
    url(r'^mission$', views.mission, name='mission'),
    #url(r'password_recovery$', views.password_recovery, name='password_recovery'),
    url(r'^register', views.register, name='register'),
    #url(r'request_translation/(?P<class_type>[^\./]+)/(?P<class_id>[^\./]+)', views.request_translation),
    #url(r'roadmap/', views.roadmap, name='roadmap'),
    #url(r'stats', views.stats, name='stats'),
    url(r'start_link$', views.start_link, name='start_link'),
    url(r'start_link_to_file$', views.start_link_to_file, name='start_link_to_file'),
    url(r'team$', views.team, name='team'),
    #url(r'test/', views.test, name='test'),
    url(r'thanks/', views.thanks, name='thanks'),
    url(r'^upload$', views.upload, name='upload'),
    url(r'^upload_file$', views.upload_file, name='upload_file'),
    url(r'view_map/(?P<job>[^/]+)', views.view_map, name='view_map'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth'))
]

# add urls for static content
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
