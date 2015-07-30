from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('', 
	url(r'get_years/$', views.hcone_get_years),
	url(r'get_storms/(?P<year>.+)/$', views.hcone_get_storms),
	url(r'get_storm_info/(?P<year>.+)/(?P<storm>.+)/$', views.hcone_get_storm_info),
	url(r'get_storm_contours/(?P<year>.+)/(?P<storm>.+)/$', views.hcone_get_storm_contours),
	url(r'contour_viewer/$', views.hcone_contour_viewer),
) 
