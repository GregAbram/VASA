var osm;
var map;
var eps4326; 
var dataLayer;
var track = -1;
var track_feature = -1;
var clon, clat;
var storm = -1;
var year  = -1;

function receive_storm_list(data)
{
	if (data['status'] != 'OK')
	    alert('Error: ' + data['status']);
	else
	{
	    result= data['result']
	    h = '<option name=storm_option value="ignore">Select</option>'
	    for (var s in result)
	    {
		storm = result[s];
		n = storm['name'];
		if (n != 'UNNAMED')
		{
		    label = n + ' ' + storm['year'];
		    h = '<option name=storm_option value="' + label + '">' + label + '</option>' + h;
		}
	    }
	    document.getElementById('storm_selector').innerHTML = h;
	}
}

function receive_track(data)
{
  	if (data['status'] != 'OK')
	    alert('Error: ' + data['status']);
        else
	{
	    track = data['result'];
	    redraw();
	}
}

function redraw()
{
	dataLayer.removeAllFeatures()

	if (track != -1)
	{
	    clon = 0.0;
	    clat = 0.0;

	    var p_array = []
	    for (var i in track)
	    {
	        var trackpoint = track[i];

	        var lat = trackpoint['lat']
	        lat = lat.slice(0,lat.length-1)

	        var lon = trackpoint['lon'];
	        if (lon[lon.length-1] == 'W')
		    lon = '-' + lon.slice(0, lon.length-1);
	        else
		    lon = lon.slice(0, lon.length-1);

	        clon = clon + parseFloat(lon)
	        clat = clat + parseFloat(lat)

	        var p = new OpenLayers.Geometry.Point(lon, lat).transform(eps4326, osm.projection);
	        p_array.push(p);
	    }

	    clon = clon / track.length
	    clat = clat / track.length

	    var l = new OpenLayers.Geometry.LineString(p_array);
	    track_feature = new OpenLayers.Feature.Vector(l, null, {strokeColor: "#ff0000"});
	}

	if (track_feature != -1)
	{
	    features = [track_feature]
	    dataLayer.addFeatures(features);
	    dataLayer.redraw();

	    map.setCenter(new OpenLayers.LonLat(clon, clat).transform(eps4326, osm.projection), 3);
	}
}

function get_track(data)
{
	if (data != 'ignore')
	{
	    tt = data.split(" ");
	    storm = tt[0];
	    year = tt[1];
	    var u = '/track/track/' + year + '/' + storm;
	    $.ajax({url: u, dataType: 'json', cache: false, success: receive_track});
	}
}

$(document).ready(function() {

	map = new OpenLayers.Map("map");
	osm = new OpenLayers.Layer.OSM();
	map.addLayers([osm]);
    
	dataLayer = new OpenLayers.Layer.Vector("DataLayer");	
	map.addLayers([dataLayer]);

	map.zoomToMaxExtent();

	eps4326 = new OpenLayers.Projection("EPSG:4326");

 	$.ajax({url: '/track/list', dataType: 'json', cache: false, success: receive_storm_list});
});
