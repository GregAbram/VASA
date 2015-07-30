import sys, h5py, numpy, sqlite3, os, datetime, time, math, calendar, struct, array, zlib, pdb
import StringIO
from random import random
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, Template
from scipy.interpolate import interp1d, UnivariateSpline
from scipy.spatial import Delaunay

VASA_DATADIR='/var/data'
WINDRADII_DATADIR=VASA_DATADIR + '/windradii_data'

@login_required
def contour_viewer(request):
     return render(request, 'windradii_viewer.html', {})

@login_required
def get_years(request):
	try:
	    years = sorted(os.listdir(WINDRADII_DATADIR))
	    return HttpResponse(simplejson.dumps({'status': 'OK', 'result': years}), mimetype = u'application/json')
	except:
	    return HttpResponse(simplejson.dumps({'status': 'unable to access year list from %s' % WINDRADII_DATADIR}), mimetype = u'application/json')

@login_required
def get_storms(request, year):
	try:
	    storms = sorted(os.listdir(WINDRADII_DATADIR + '/' + year))
	    return HttpResponse(simplejson.dumps({'status': 'OK', 'result': storms}), mimetype = u'application/json')
	except:
	    return HttpResponse(simplejson.dumps({'status': 'unable to access storm list for year ' + year}), mimetype = u'application/json')
	    
@login_required
def get_storm_info(request, year, storm):
    
	try:
	    gms = os.listdir(WINDRADII_DATADIR + '/' + year)
	    timestamps = [time.strftime('%Y-%b-%d %H:%M:%S %Z', time.gmtime(t)) for t in sorted(gms)]
	    return HttpResponse(simplejson.dumps({'status': 'OK', 'result': timestamps}), mimetype = u'application/json')
	except:
	    return HttpResponse(simplejson.dumps({'status': 'unable to access storm timestamps for year ' + year + ' and storm ' + storm}), mimetype = u'application/json')

@login_required
def get_storm_contours(request, year, storm):
    sys.stderr.write('WINDRADII\n')
    try:
	dir = WINDRADII_DATADIR + "/" + year + "/" + storm

	data = []
	for f in sorted(os.listdir(dir)):
	    fo = open(dir + '/' + f, 'r')
	    counts = [int(i) for i in fo.readline().strip().split(' ')]
	    data.append({'timestamp': f, 'contours': [[[float(i) for i in fo.readline().strip().split(' ')] for j in range(k)] for k in counts]})
	    fo.close()

	return HttpResponse(simplejson.dumps({'status': 'OK', 'result': data}), mimetype = u'application/json')
    except:
	return HttpResponse(simplejson.dumps({'status': 'unable to access track for dataset ' + dataset + ' in storm ' + storm + '/' + year}), mimetype = u'application/json')

