import sys, h5py, numpy, sqlite3, os, datetime, time, math, calendar, struct, array, zlib
import pdb
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
GRID_DATADIR=VASA_DATADIR + '/grid_data'

def cvt_time(s):
       t = calendar.timegm(time.strptime(s, '%Y-%m-%d %H:%M:%SZ'))
       return t / (60.0 * 60.0)

Radii_12Hr = [0.0, 33.0, 52.0, 72.0, 92.0, 128.0, 177.0, 229.0]

@login_required
def track_viewer(request):
     return render(request, 'track_viewer.html', {})

@login_required
def get_years(request):
	try:
	    years = os.listdir(GRID_DATADIR)
	    return HttpResponse(simplejson.dumps({'status': 'OK', 'result': years}), mimetype = u'application/json')
	except:
	    return HttpResponse(simplejson.dumps({'status': 'unable to access year list from %s' % GRID_DATADIR}), mimetype = u'application/json')

@login_required
def get_storms(request, year):
	try:
	    storms = os.listdir(GRID_DATADIR + '/' + year)
	    return HttpResponse(simplejson.dumps({'status': 'OK', 'result': storms}), mimetype = u'application/json')
	except:
	    return HttpResponse(simplejson.dumps({'status': 'unable to access storm list for year ' + year}), mimetype = u'application/json')
	    
@login_required
def get_storm_info(request, year, storm):

	result = []
	
	for dataset in sorted(os.listdir(GRID_DATADIR + '/' + year + '/' + storm + '/consensus')):
	    f = GRID_DATADIR + '/' + year + '/' + storm + '/consensus/' + dataset + '/fort.63.nc'
	    try:
	      h = h5py.File(f, 'r')
	      try:
		  t0 = datetime.datetime.strptime(h['time'].attrs['units'][len('seconds since '):], '%Y-%m-%d %H:%M:%S +00:00')
	      except:
		  try:
		      t0 = datetime.datetime.strptime(h['time'].attrs['units'][len('seconds since '):], '%Y-%m-%d %H:%M:%S')
		  except: 
		      raise

	      times = []
	      for t in h['time']:
		times.append(str(t0 + datetime.timedelta(seconds=t)))

	      vars = ['depth(1)', 'zeta(%d)' %  h['zeta'].shape[0]]
	      h.close()

	      try:
		  f = GRID_DATADIR + '/' + year + '/' + storm + '/consensus/' + dataset + '/fort.64.nc'
		  h = h5py.File(f, 'r')
		  vars.append('current(%d)' % h['u-vel'].shape[0])
		  h.close()
	      except:
		  pass

	      try:
		  f = GRID_DATADIR + '/' + year + '/' + storm + '/consensus/' + dataset + '/fort.73.nc'
		  h = h5py.File(f, 'r')
		  vars.append('pressure(%d)' % h['pressure'].shape[0])
		  h.close()
	      except:
		  pass

	      try:
		  f = GRID_DATADIR + '/' + year + '/' + storm + '/consensus/' + dataset + '/fort.74.nc'
		  h = h5py.File(f, 'r')
		  vars.append('wind(%d)' % h['windx'].shape[0])
		  h.close()
	      except:
		  pass

	      result.append([dataset, vars, times])

	    except:
	      pass

	return HttpResponse(simplejson.dumps({'status': 'OK', 'result': result}), mimetype = u'application/json')

@login_required
def get_track(request, year, storm, dataset):
    try:
	filename = GRID_DATADIR + "/" + year + "/" + storm + "/consensus/" + dataset + "/track.csv"
	file = open(filename, "r")
	track = []
	for f in file:
		f = f.strip().split(',')
		if len(f) == 3:
		    f = [float(i) for i in f]
		    track.append((f[0], [f[1], f[2]]))
	file.close()
	return HttpResponse(simplejson.dumps({'status': 'OK', 'result': track}), mimetype = u'application/json')
    except:
	return HttpResponse(simplejson.dumps({'status': 'unable to access track for dataset ' + dataset + ' in storm ' + storm + '/' + year}), mimetype = u'application/json')

@login_required
def get_shape(request, year, storm, dataset):
    try:
	filename = GRID_DATADIR + "/" + year + "/" + storm + "/consensus/" + dataset + "/track.csv"
	file = open(filename, "r")
	time = []
	x = []
	y = []
	for f in file:
		f = f.strip().split(',')
		if len(f) == 3:
		    f = [float(i) for i in f]
		    time.append(float(f[0]) / 3600)
		    x.append(float(f[1]))
		    y.append(float(f[2]))
	file.close()
    except:
	return HttpResponse(simplejson.dumps({'status': 'unable to access track for dataset ' + dataset + ' in storm ' + storm + '/' + year}), mimetype = u'application/json')

    time = [0] + [i-time[0] for i in time[1:]]

    max_time = 12*(len(Radii_12Hr) - 1)

    if time[-1] < max_time:
	 max_time = time[-1]

    t_interp = [max_time * (i/64.0) for i in range(64)]

    x_smoother = UnivariateSpline(time, x, w=([999] + [1 for t in time[1:]]), s=len(time))
    y_smoother = UnivariateSpline(time, y, w=([999] + [1 for t in time[1:]]), s=len(time))
    x = x_smoother(t_interp)
    y = y_smoother(t_interp)

    tt = [x[0]] + x + [x[-1]]
    dx = [j-i for i,j in zip(tt[:-2], tt[2:])]

    tt = [y[0]] + y + [y[-1]]
    dy = [j-i for i,j in zip(tt[:-2], tt[2:])]

    tt = [x[0]] + x + [x[-1]]

    rx = [i + j for i,j in zip(x,dy)]
    ry = [i - j for i,j in zip(y,dx)]

    # Use those to figure out scaling  - the following gives the distance between
    # each point and a point along its perpendicular in NM
    cosPhi = [math.cos((math.radians(i) + math.radians(j)) / 2.0) for i,j in zip(y,ry)]
    a = [(math.radians(i) - math.radians(j))*k for i,j,k in zip(x,rx,cosPhi)]
    b = [(math.radians(i) - math.radians(j)) for i,j in zip(y,ry)]
    d  = [3440.07 * math.sqrt(i*i + j*j) for i,j in zip(a,b)]

    # The following gives the desired distance in NM
    rfunc = interp1d([12.0 * i for i in range(len(Radii_12Hr))], Radii_12Hr)
    r = [rfunc(t) for t in t_interp]

    # scaling is the ratio of the desired radius to the radius given by the 
    # calculation of the perpendicular vector above
    s = [0 if j == 0 else i/j for i,j in zip(r, d)]

    r = [(t, [_x+(_dy*_s), _y-(_dx*_s)]) for t,_x,_dx,_y,_dy,_s in zip(time, x, dx, y, dy, s)]
    l = [(t, [_x-(_dy*_s), _y+(_dx*_s)]) for t,_x,_dx,_y,_dy,_s in zip(time, x, dx, y, dy, s)]
    
    r.reverse()
    shape = l + r

    j = simplejson.dumps({'status': 'OK', 'result': shape})
    return HttpResponse(j, mimetype = u'application/json')

def add_component(f, shape, data):
    hdrfmt = 'ciii'
    hdrsz = struct.calcsize(hdrfmt)
    a = array.array('B', zlib.compress(array.array(f, data.flatten())))
    bytes.extend(struct.pack(hdrfmt, f, shape[0], shape[1], len(a)))
    bytes.extend(a)

def pack_grid(grid):

    bytes = bytearray()

    bytes.extend(struct.pack('i', len(grid)))

    for v in grid:

	v = str(v)
        l = len(v) + 1
        bytes.extend(struct.pack('i%ds' % l, l, v))

	f     = grid[v][0]
	shape = grid[v][1]
	data  = grid[v][2]

	hdrfmt = 'ciii'
	hdrsz = struct.calcsize(hdrfmt)
	a = array.array('B', zlib.compress(array.array(f, data.flatten())))
	bytes.extend(struct.pack(hdrfmt, f, shape[0], shape[1], len(a)))
	bytes.extend(a)

    return bytes
    
def pull_grid(name, year, dataset, timestep, longitude_range, latitude_range, variables):

    variables = variables.split(',')

    longitude_range = [float(i) for i in longitude_range.split(',')]
    latitude_range = [float(i) for i in latitude_range.split(',')]

    datadir = GRID_DATADIR + "/" + year + "/" + name + "/consensus/" + dataset  

    try:
	fname = datadir + "/fort.63.nc"
	ds = open(fname, 'r') 
	ds.close()
    except:
	return HttpResponse(simplejson.dumps({'status': 'Unable to TEST open mesh file: ' + fname}), mimetype = u'application/json')

    try:
	fname = datadir + "/fort.63.nc"
	ds = h5py.File(fname, 'r')
    except:
	return HttpResponse(simplejson.dumps({'status': 'Unable to open mesh file: ' + fname}), mimetype = u'application/json')

    try:
	x = numpy.array(ds['x'])
	y = numpy.array(ds['y'])
	triangles = numpy.array(ds['element']) - 1

	num_points = x.shape[0]
	num_triangles = triangles.shape[0]

	latlon_range_flags = numpy.array((x > longitude_range[0]) & (x < longitude_range[1]) & (y > latitude_range[0]) & (y < latitude_range[1]))
	kept_triangle_flags = latlon_range_flags[triangles[:,0]] | latlon_range_flags[triangles[:,1]] | latlon_range_flags[triangles[:,2]]
	deleted_triangle_indices = (numpy.array(range(1, num_triangles+1)) * (1-kept_triangle_flags)) - 1

	triangles = numpy.delete(triangles, deleted_triangle_indices, 0)

	reffed_points = numpy.unique(triangles)
	points = numpy.dstack((x[reffed_points], y[reffed_points]))[0]

	pointmap = numpy.repeat(0, num_points)
	pointmap[reffed_points] = 1
	pointmap = numpy.cumsum(pointmap) - 1
	triangles = pointmap[triangles]

	ds.close()
    except:
	return HttpResponse(simplejson.dumps({'status': 'Unable to access mesh file: ' + fname}), mimetype = u'application/json')

    num_output_points = len(reffed_points)
    num_output_triangles = len(triangles)

    grid = {}
    grid['vertices']  = ['f', [num_output_points, 2], points]
    grid['triangles'] = ['i', [num_output_triangles, 3], triangles]

    for v in variables:
	v = str(v)

        if v == 'depth':
	    try:
		ds = h5py.File(datadir + "/fort.63.nc", 'r')
		# grid['depth']  = ['f', [num_output_points, 1], numpy.array(ds['depth'][int(timestep)])[reffed_points]]
		grid['depth']  = ['f', [num_output_points, 1], numpy.array(ds['depth'])[reffed_points]]
		ds.close()
	    except:
		pass

        if v == 'zeta':
	    try:
		ds = h5py.File(datadir + "/fort.63.nc", 'r')
		grid['zeta']  = ['f', [num_output_points, 1], numpy.array(ds['zeta'][int(timestep)])[reffed_points]]
		ds.close()
	    except:
		pass

        if v == 'pressure':
	    try:
		ds = h5py.File(datadir + "/fort.73.nc", 'r')
		grid['pressure']  = ['f', [num_output_points, 1], numpy.array(ds['pressure'][int(timestep)])[reffed_points]]
		ds.close()
	    except:
		pass

	if v == 'wind':
	    try:
		ds = h5py.File(datadir + "/fort.74.nc", 'r')
		wx = ds['windx'][int(timestep)][reffed_points]
		wy = ds['windy'][int(timestep)][reffed_points]
		wind = numpy.dstack((wx, wy))[0]
		grid['wind']  = ['f', [num_output_points, 2], wind]
		ds.close()
	    except:
		pass

	if v == 'current':
	    try:
		ds = h5py.File(datadir + "/fort.64.nc", 'r')
		cx = list(ds['currx'][int(timestep)][reffed_points])
		cy = list(ds['curry'][int(timestep)][reffed_points])
		curr = numpy.dstack((cx, cy))[0]
		grid['current']  = ['f', [num_output_points, 2], curr]
		ds.close()
	    except:
		pass
	
    return grid

@login_required
def get_grid(request, name, year, dataset, timestep, longitude_range, latitude_range, variables):
	
    gridx  = pull_grid(name, year, dataset, timestep, longitude_range, latitude_range, variables)
    bytes = pack_grid(gridx)

    r = HttpResponse()
    r.write(bytes)
    return r

def simplify_grid(grid, num_samples):

    vertices = grid['vertices']

    lons = vertices[2][:,0]
    lats = vertices[2][:,1]

    min_lon = min(lons)
    max_lon = max(lons)

    min_lat = min(lats)
    max_lat = max(lats)

    ilons = (numpy.clip(((num_samples) * (lons - min_lon)/(max_lon - min_lon)), 0, num_samples-1)).astype(int)
    ilats = (numpy.clip(((num_samples) * (lats - min_lat)/(max_lat - min_lat)), 0, num_samples-1)).astype(int)

    bin_indices = num_samples*ilats + ilons
    bin_counts  = numpy.zeros(num_samples*num_samples)

    for i in bin_indices:
	bin_counts[i] += 1

    keepers = numpy.nonzero(bin_counts)[0]

    dlon = (max_lon - min_lon) / (num_samples+1)
    dlat = (max_lat - min_lat) / (num_samples+1)

    bin_center_lon = numpy.linspace(min_lon + (dlon/2), max_lon - (dlon/2), num_samples)
    bin_center_lat = numpy.linspace(min_lat + (dlat/2), max_lat - (dlat/2), num_samples)

    xx,yy = numpy.meshgrid(bin_center_lon, bin_center_lat)
    gridpoints = numpy.dstack((xx.flatten(), yy.flatten()))[0][keepers,:]

    triangles = numpy.array(Delaunay(gridpoints).simplices.copy())

    newgrid = {}
    newgrid['vertices']  = ['f', [len(gridpoints), 2], gridpoints]
    newgrid['triangles'] = ['i', [len(triangles), 3], triangles]

    for varname in grid:
	if varname == 'triangles' or varname == 'vertices': continue
	var = grid[varname][2]
        if len(var.shape) == 2: width = var.shape[1]
        else: width = 1
	accum = numpy.zeros(num_samples*num_samples*width).reshape(num_samples*num_samples, width)
	for i,v in zip(bin_indices, var):
	    accum[i] += v
	for i,k in enumerate(bin_counts):
	    if k > 0: accum[i] /= k
	newgrid[varname] = ['f', [len(keepers), width], accum[keepers]]

    return newgrid

@login_required
def get_simplified_grid(request, name, year, dataset, timestep, longitude_range, latitude_range, variables, simplification):

    grid  = pull_grid(name, year, dataset, timestep, longitude_range, latitude_range, variables)
    simplified_grid = simplify_grid(grid, int(simplification))
    bytes = pack_grid(simplified_grid)

    r = HttpResponse()
    r.write(bytes)
    return r
