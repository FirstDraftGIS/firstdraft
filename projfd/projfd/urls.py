import appfd, inspect
from apifd.views import redirect_to_api
from appfd.models import Basemap
from appfd import views
#from controlcenter.views import controlcenter
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.auth.models import User, Group
from django.contrib.gis import admin
from django.conf import settings
from rest_framework_swagger.views import get_swagger_view

urlpatterns = [
    #url(r'^appfd/', include('appfd.urls')),l
    url(r'^api$', redirect_to_api),
    url(r'^api/', include('apifd.urls')),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^swagger/', get_swagger_view(title='First Draft GIS API')),
    #url(r'^silk/', include('silk.urls', namespace='silk')),
    #url(r'^help/', include('help.urls')),
    url(r'^$', views.index, name="index"),
    #url(r'activate/(?P<key>[^\./]+)$', views.activate, name='activate'),
    url(r'^admin/', admin.site.urls),
    #url(r'^admin/dashboard/', controlcenter.urls),
    #url(r'change_email$', views.change_email, name='change_email'),
    #url(r'change_password$', views.change_password, name='change_password'),
    url(r'^contact$', views.contact, name='contact'),
    url(r'^request_map_from_sources$', views.request_map_from_sources, name="request_map_from_sources"),
    url(r'^does_map_exist/(?P<job>[^/]+)/(?P<extension>[^/]+)$', views.does_map_exist, name='does_map_exist'),
    url(r'^does_metadata_exist/(?P<job>[^/]+)/(?P<_type>[^/]+)$', views.does_metadata_exist, name='does_metadata_exist'),
    url(r'^disclaimers$', views.disclaimers, name='disclaimers'),
    url(r'^get_map/(?P<job>[^/]+)/(?P<extension>[^/]+)$', views.get_map, name='get_map'),
    url(r'^get_metadata/(?P<job>[^/]+)/(?P<metadata_type>[^/]+)$', views.get_metadata, name='get_metadata'),
    url(r'^maps/(?P<job>[^/]+)$', views._map, name='_map'),
    url(r'^mission$', views.mission, name='mission'),
    #url(r'password_recovery$', views.password_recovery, name='password_recovery'),
    url(r'preview_map/(?P<job>[^/]+)', views.preview_map, name='preview_map'),
    url(r'^register', views.register, name='register'),
    url(r'view_map/(?P<job>[^/]+)', views.view_map, name='view_map'),
    url(r'view_frequency_map/(?P<job>[^/]+)', views.view_frequency_map, name='view_frequency_map'),
]

# add urls for static content
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
