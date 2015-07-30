import os, sys, math, calendar, time, sqlite3
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import simplejson

# import h5py, numpy, sqlite3, os, math, calendar, time
# from django.template import RequestContext, Template
# from django.utils import simplejson
# from numpy import array as na
# from scipy.interpolate import interp1d

VASA_DATADIR='/var/data'
TRACK_DATADIR=VASA_DATADIR + '/track_data'

@login_required
def view(request):
    return render(request, 'viewer.html', {})

@login_required
def list(request):
    d = sqlite3.connect(TRACK_DATADIR + "/hurricanes.db")
    c = d.cursor()
    c.execute('select name, date from storms order by date')
    r = []
    for name, date in c:
        r.append({'name': name, 'year': date[:4]})
    j = simplejson.dumps({'status': 'OK', 'result': r})
    return HttpResponse(j, mimetype = u'application/json')

@login_required
def track(request, year, name):
    try:
	y = year[:4] + "%"
	d = sqlite3.connect(TRACK_DATADIR + "/hurricanes.db")
	c = d.cursor()
	c.execute('select id from storms where name == "%s" and date like "%s"' % (name, y))
	id = c.fetchone()[0]
	fixes = []
	c.execute('select fixtime, lat, lon, maxwind, min_pressure from fixes where storm == %s order by fixtime' % id)
	for t,lat,lon,w,p in c:
	    fixes.append({'time': t, 'lat': lat, 'lon': lon, 'max wind': w, 'min pressure': p})
	j = simplejson.dumps({'status': 'OK', 'result': fixes})
	return HttpResponse(j, mimetype = u'application/json')
    except:
	j = simplejson.dumps({'status': 'No storm named %s in year %s' % (name, year)})
	return HttpResponse(j, mimetype = u'application/json')
	
