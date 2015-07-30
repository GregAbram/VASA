import os, sys, pdb
from django.contrib import admin
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.conf.urls.defaults import patterns, include, url
from django.utils import simplejson
from django.template import RequestContext
from django.http import HttpResponseRedirect

admin.autodiscover()

from vasa.adcirc import urls
from vasa.windradii import urls
from vasa.hcone import urls

def vasa_login(request):

    if request.POST:

	username = request.POST['username']
	password = request.POST['password']

	user = authenticate(username=username, password=password)

	if user is not None:

	    if user.is_active:
		login(request, user)
		return render_to_response('welcome.html', {'state': 'success', 'username': ''}, context_instance=RequestContext(request))
	    else:
		return render_to_response('auth.html', {'state': 'inactive account', 'username': ''}, context_instance=RequestContext(request))
	else:
	    return render_to_response('auth.html', {'state': 'bad username/password', 'username': ''}, context_instance=RequestContext(request))
	    state = 'bad username/password'

    return render_to_response('auth.html', {'state': 'login: ', 'username': ''}, context_instance=RequestContext(request))

urlpatterns = patterns('',
    url(r'^$', vasa_login),
    url(r'^track/', include('vasa.track.urls')),
    url(r'^adcirc/', include('vasa.adcirc.urls')),
    url(r'^windradii/', include('vasa.windradii.urls')),
    url(r'^hcone/', include('vasa.hcone.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),)

