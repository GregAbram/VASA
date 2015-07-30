var osm;
var map;
var eps4326; 
var dataLayer;

var clon, clat;
var timesteps = [];
var theAnimator;

function receive_years(data)
{
	year  = $('#hcone_year_selector').val()

	if (data['status'] != 'OK')
	    alert('Error: ' + data['status']);
	else
	{
	    result = data['result']
	    h = '<option name=hcone_year_option value="ignore">Select</option>'
	    for (var s in result)
	    {
		year = result[s];
		h = h + '<option name=hcone_year_option value="' + year + '">' + year + '</option>';
	    }
	    $('#hcone_year_selector').html(h);
	}
}

function receive_storms(data)
{
	year  = $('#hcone_year_selector').val()
	storm = $('#hcone_storm').val()

	if (data['status'] != 'OK')
	    alert('Error: ' + data['status']);
	else
	{
	    result = data['result']
	    h = '<option name=hcone_storm_option value="ignore">Select</option>'
	    for (var s in result)
	    {
		storm = result[s];
		h = h + '<option name=hcone_storm_option value="' + storm + '">' + storm + '</option>';
	    }
	    $('#hcone_storm_selector').html(h);
	    $('#hcone_storm_selection').show();
	}
}

function receive_contours(data)
{
  	if (data['status'] != 'OK')
	    alert('Error: ' + data['status']);
        else
	{
	    timesteps = data['result'];
	    
	    clat = 0;
	    clon = 0;

	    knt = 0;
	    for (var t in timesteps)
	    {
		timestep = timesteps[t];
		for (var c in timestep['contours'])
		{
		   contour = timestep['contours'][c];
		   for (var p in contour)
		   {
			pt = contour[p];
			clon = clon + pt[0];
			clat = clat + pt[1];
			knt ++;
		   }
		}
	    }

	    clon = clon / knt;
	    clat = clat / knt;


	    timestamps = []
	    for (var i = 0; i < timesteps.length; i++)
		timestamps.push(i)

	    theAnimator.SetTimeFrame(0, timesteps.length);
	    theAnimator.SetSteps(timesteps.length);

	    map.setCenter(new OpenLayers.LonLat(clon, clat).transform(eps4326, osm.projection), 5);

	    theAnimator.Show()
	    theAnimator.Do(0);
	}
}

var colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'];

function redraw(n)
{
	dataLayer.removeAllFeatures()

	features = []

	timestep = timesteps[n];
	for (var c in timestep['contours'])
	{
	    contour = timestep['contours'][c];

	    ptArray = [];
	    for (var p in contour)
	    {
		pt = contour[p];
		g = new OpenLayers.Geometry.Point(pt[0], pt[1]).transform(eps4326, osm.projection);
		ptArray.push(g)
  	    }
	    pt = contour[0];
	    g = new OpenLayers.Geometry.Point(pt[0], pt[1]).transform(eps4326, osm.projection);
	    ptArray.push(g)

	    ls = new OpenLayers.Geometry.LineString(ptArray);
	    f = new OpenLayers.Feature.Vector(ls, null, {strokeColor: colors[c], strokeOpacity: 1, strokeWidth: 2});
	    features.push(f);
	}

	dataLayer.addFeatures(features);
	dataLayer.redraw();

}

function get_storms(year)
{
	year  = $('#hcone_year_selector').val()
	var u = '/hcone/get_storms/' + year;
	$.ajax({url: u, dataType: 'json', cache: false, success: receive_storms});
}

function get_storm_contours()
{
	year  = $('#hcone_year_selector').val()
	storm = $('#hcone_storm_selector').val()
	var u = '/hcone/get_storm_contours/' + year + '/' + storm;
	$.ajax({url: u, dataType: 'json', cache: false, success: receive_contours});
}

$(document).ready(function() {

	map = new OpenLayers.Map("map");
	osm = new OpenLayers.Layer.OSM();
	map.addLayers([osm]);
    
	dataLayer = new OpenLayers.Layer.Vector("DataLayer");	
	map.addLayers([dataLayer]);

	map.zoomToMaxExtent();

	eps4326 = new OpenLayers.Projection("EPSG:4326");

 	$.ajax({url: '/hcone/get_years', dataType: 'json', cache: false, success: receive_years});

	theAnimator = new AnimationControl(redraw);
        var animator_ui = theAnimator.GetUI();
        animator_ui.css('position', 'absolute');
        animator_ui.css('top', '0px');
        animator_ui.css('right', '0px');
        animator_ui.css('z-index', '1001');
        $('#map').append(animator_ui);
});
