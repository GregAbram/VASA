from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('', 
	url(r'get_years/$', views.get_years),
	url(r'get_storms/(?P<year>.+)/$', views.get_storms),
	url(r'get_storm_info/(?P<year>.+)/(?P<storm>.+)/$', views.get_storm_info),
	url(r'get_track/(?P<year>.+)/(?P<storm>.+)/(?P<dataset>.+)/$', views.get_track),
	url(r'get_shape/(?P<year>.+)/(?P<storm>.+)/(?P<dataset>.+)/$', views.get_shape),
	url(r'get_grid/(?P<name>.+)/(?P<year>.+)/(?P<dataset>.+)/(?P<timestep>.+)/(?P<longitude_range>.+)/(?P<latitude_range>.+)/(?P<variables>.+)/$', views.get_grid),
	url(r'get_simplified_grid/(?P<name>.+)/(?P<year>.+)/(?P<dataset>.+)/(?P<timestep>.+)/(?P<longitude_range>.+)/(?P<latitude_range>.+)/(?P<variables>.+)/(?P<simplification>.+)/$', views.get_simplified_grid),
	url(r'track_viewer/$', views.track_viewer),
) 
