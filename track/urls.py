from django.conf.urls.defaults import patterns, include, url

import views

urlpatterns = patterns('', 
	url(r'view/$', views.view),
	url(r'list/$', views.list),
	url(r'track/(?P<year>.+)/(?P<name>.+)/$', views.track),
) 

