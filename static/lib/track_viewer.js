var map;
var eps4326; 
var dataLayer;

var year = -1
var storm = -1
var dataset = -1
var track = -1;

var clon, clat;

function receive_year_list(data)
{
	if (data['status'] != 'OK')
	    alert('Error: ' + data['status']);
	else
	{
	    result = data['result']
	    h = '<option name=adcirc_year_option value="ignore">Select</option>'
	    for (var s in result)
	    {
		year = result[s];
		h = h + '<option name=adcirc_year_option value="' + year + '">' + year + '</option>';
	    }
	    document.getElementById('adcirc_year_selector').innerHTML = h;
	}
}

function receive_storm_list(data)
{
	if (data['status'] != 'OK')
	    alert('Error: ' + data['status']);
	else
	{
	    result = data['result']
	    h = '<option name=adcirc_storm_option value="ignore">Select</option>'
	    for (var s in result)
	    {
		storm = result[s];
		h = h + '<option name=adcirc_storm_option value="' + storm + '">' + storm + '</option>';
	    }
	    $('#adcirc_storm_selector').html(h);
	    $('#adcirc_storm_selection').show();
	}
}

function receive_dataset_list(data)
{
	if (data['status'] != 'OK')
	    alert('Error: ' + data['status']);
	else
	{
	    result = data['result']
	    h = '<option name=adcirc_dataset_option value="ignore">Select</option>'
	    for (var s in result)
	    {
		ds = result[s];
		h = h + '<option name=adcirc_dataset_option value="' + ds[0] + '">' + ds[2][0] + '</option>';
	    }
	    $('#adcirc_dataset_selector').html(h);
	    $('#adcirc_dataset_selection').show();
	}
}

function receive_track(data)
{
  	if (data['status'] != 'OK')
	    alert('Error: ' + data['status']);
        else
	{
	    clat = 0;
	    clon = 0;
		
	    pt_array = [];
	    p = data['result'];
	    for (var i in p)
	    {
		pi = p[i];
		clon = clon + pi[1][0];
		clat = clat + pi[1][1];
		pt_array.push(new OpenLayers.Geometry.Point(pi[1][0], pi[1][1]).transform(eps4326, osm.projection));
	    }
	    clon = clon / p.length;
	    clat = clat / p.length;
	    l = new OpenLayers.Geometry.LineString(pt_array);
	    track = new OpenLayers.Feature.Vector(l, null, {strokeColor: '#ff0000'});
	    redraw();
	}
}

function redraw()
{
	dataLayer.removeAllFeatures()

	if (track != -1)
	{
	    features = [track];

	    dataLayer.addFeatures(features);
	    dataLayer.redraw();

	    map.setCenter(new OpenLayers.LonLat(clon, clat).transform(eps4326, osm.projection), 5);
	}
}

var storm = -1;
var year  = -1;
var t_now = 0;

function get_storm_list(data)
{
	if (data != 'ignore')
	{
	    year = data;
	    $('#dataset_selection').hide();
	    var u = '/adcirc/get_storms/' + data;
	    $.ajax({url: u, dataType: 'json', cache: false, success: receive_storm_list});
	}
}

function get_dataset_list(data)
{
	if (data != 'ignore')
	{
	    storm = data;
	    var u = '/adcirc/get_storm_info/' + year + '/' + data;
	    $.ajax({url: u, dataType: 'json', cache: false, success: receive_dataset_list});
	}
}

function get_track(data)
{
	dataset = data;
	if ($('#shapeflag').is(':checked'))
	    u = '/adcirc/get_shape/' + year + '/' + storm + '/' + data;
	else
	    u = '/adcirc/get_track/' + year + '/' + storm + '/' + data;
 	$.ajax({url: u, dataType: 'json', cache: false, success: receive_track});
	t_now += 4.0;
}

$(document).ready(function() {

	map = new OpenLayers.Map("map");
	osm = new OpenLayers.Layer.OSM();
	map.addLayers([osm]);
    
	dataLayer = new OpenLayers.Layer.Vector("DataLayer");	
	map.addLayers([dataLayer]);

	map.zoomToMaxExtent();

	eps4326 = new OpenLayers.Projection("EPSG:4326");

 	$.ajax({url: '/adcirc/get_years', dataType: 'json', cache: false, success: receive_year_list});
});
