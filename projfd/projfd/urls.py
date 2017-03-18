import appfd, inspect
from appfd.models import Basemap
from appfd import views
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.auth.models import User, Group
from django.contrib.gis import admin
from django.conf import settings

#initialize urlpatterns
urlpatterns = []

# add most urls
urlpatterns += [
    #url(r'^appfd/', include('appfd.urls')),
    url(r'^api/', include('apifd.urls')),
    #url(r'^help/', include('help.urls')),
    url(r'^$', views.index, name="index"),
    #url(r'about$', views.about, name='about'),
    #url(r'activate/(?P<key>[^\./]+)$', views.activate, name='activate'),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'change_email$', views.change_email, name='change_email'),
    #url(r'change_password$', views.change_password, name='change_password'),
    url(r'^contact$', views.contact, name='contact'),
    url(r'^request_map_from_file$', views.request_map_from_file, name="request_map_from_file"),
    url(r'^request_map_from_text$', views.request_map_from_text, name="request_map_from_text"),
    url(r'^request_map_from_urls_to_webpages$', views.request_map_from_urls_to_webpages, name="request_map_from_urls_to_webpages"),
    url(r'^request_map_from_urls_to_files$', views.request_map_from_urls_to_files, name="request_map_from_urls_to_files"),
    url(r'^request_map_from_sources$', views.request_map_from_sources, name="request_map_from_sources"),
    url(r'^does_map_exist/(?P<job>[^/]+)/(?P<extension>[^/]+)$', views.does_map_exist, name='does_map_exist'),
    url(r'^does_metadata_exist/(?P<job>[^/]+)/(?P<_type>[^/]+)$', views.does_metadata_exist, name='does_metadata_exist'),
    url(r'^disclaimers$', views.disclaimers, name='disclaimers'),
    #url(r'login/$', views.login, name='login'),
    #url(r'logout/', views.user_logout, name='logout'),
    url(r"^embed_frequency_map/(?P<job>[^/]+)$", views.embed_frequency_map_with_job, name="embed_frequency_map_with_job"),
    url(r"^iframe$", views.iframe, name="iframe"),
    url(r'^get_map/(?P<job>[^/]+)/(?P<extension>[^/]+)$', views.get_map, name='get_map'),
    url(r'^get_metadata/(?P<job>[^/]+)/(?P<metadata_type>[^/]+)$', views.get_metadata, name='get_metadata'),
    url(r'^maps/(?P<job>[^/]+)$', views._map, name='_map'),
    url(r'^mission$', views.mission, name='mission'),
    #url(r'password_recovery$', views.password_recovery, name='password_recovery'),
    url(r'preview_map/(?P<job>[^/]+)', views.preview_map, name='preview_map'),
    url(r'^register', views.register, name='register'),
    #url(r'request_translation/(?P<class_type>[^\./]+)/(?P<class_id>[^\./]+)', views.request_translation),
    #url(r'roadmap/', views.roadmap, name='roadmap'),
    #url(r'stats', views.stats, name='stats'),
    url(r'team$', views.team, name='team'),
    #url(r'test/', views.test, name='test'),
    url(r'thanks/', views.thanks, name='thanks'),
    url(r'^verify_map/(?P<job>[^/]+)$', views.verify_map, name='verify_map'),
    url(r'view_map/(?P<job>[^/]+)', views.view_map, name='view_map'),
    url(r'view_frequency_map/(?P<job>[^/]+)', views.view_frequency_map, name='view_frequency_map'),
    url('', include('social_django.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth'))
]

# add urls for static content
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
