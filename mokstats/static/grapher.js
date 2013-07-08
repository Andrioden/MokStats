/*
* This method is a semi-hax that attempts to init the graph in
* an interval until it succeds. I was unable to trigger the method
* at the correct time.
*/
function tryToGraph(elementId, func) {
	var interval = setInterval(function(){
		try {
			func();
		}
		catch(err) {
			window.clearInterval(interval);
			alert("Failed to initiate graph: "+err);
		}
		if ($("#"+elementId).find('canvas').length > 0) {
			window.clearInterval(interval);
		}
	},100);
}

function initResultGraph(id, played, won, lost) {
	var other = played - won - lost;
	var s1 = [
	          ['Vunnet ('+won+')', won], 
	          ['Annet ('+other+')', other],
	          ['Tapt ('+lost+')', lost],
	          ];

	$.jqplot(id, [s1], {
		title:'Resultater',
		seriesColors: ['#90EE90', '#F0F03F', '#FC7E7E'],
		seriesDefaults:{
			renderer:$.jqplot.PieRenderer,
			rendererOptions: {
				showDataLabels: true
			}
		},
		legend: {
			show: true,
			rendererOptions: {
				numberRows: 1
			},
			location: 's'
		}
	});


}

function initRatingGraph(id, plotdata, clickUrl, labels) {
	// Create the dynamic label that behaves different when labels are supplied
	var customLegend = {};
	if (labels) {
		customLegend = {
				show: true,
				labels: labels,
				placement: 'outsideGrid',
				location: 'e',
				renderer: $.jqplot.EnhancedLegendRenderer,
				rendererOptions: {
					seriesToggle: "fast",
				},
		};
	}
	
	// Create graph
	var chart = $.jqplot(id, plotdata, {
		title:'Rating utvikling for aktive spillere',
		legend: customLegend,
		axes:{
			xaxis:{
				renderer:$.jqplot.DateAxisRenderer,
				tickOptions:{
					formatString:'%b&nbsp;%y'
				},
			},
			yaxis:{
				tickOptions:{
					formatString:'%.0f'
				}
			}
		},
		highlighter: {
			show: true,
			sizeAdjust: 7.5,
			yvalues: 3,
		    formatString:'<span>%s: %s <span class="smaller %s">(%s)</span></span>'
		},
		cursor: {
			show: true,
			zoom:true,
		}
	});
	
	//Can navigate to the match by clicking the chart point.
	$("#"+id).on("jqplotDataClick", function(ev, seriesIndex, pointIndex, data) {
		$.mobile.changePage(clickUrl+data[4]+"/");
	});
	
	$(window).resize(function() {
		$("#"+id).width($(window).width()-20);
		chart.replot( {resetAxes: ['xaxis'] } );
    });
}

function initActivityGraph(id, data, places) {
	var chart = $.jqplot(id, data,{
		stackSeries: true,
		showMarker: false,
		highlighter: {
			show: true,
			showTooltip: false
		},
		seriesDefaults: {
			fill: true,
		},
		legend: {
			show: true,
			placement: 'outsideGrid',
			location: 's',
			labels: places,
			renderer: $.jqplot.EnhancedLegendRenderer,
			rendererOptions: {
				seriesToggle: "fast",
				numberRows: 1,
			},
		},
		grid: {
			drawBorder: false,
			shadow: false
		},
		axes: {
			xaxis: {
				renderer:$.jqplot.DateAxisRenderer,
				tickOptions: {
					formatString:'%b&nbsp;%y',
				},
			},
			yaxis: {min:0},
		},
		highlighter: {
			show: true,
			sizeAdjust: 7.5,
		    formatString:'<span>%s</span>'
		},
		cursor: {
			show: true,
			zoom:true,
		},
	});
	
	$(window).resize(function() {
		$("#"+id).width($(window).width()-20);
		chart.replot( {resetAxes: ['xaxis'] } );
    });
}

/*
var utils = {
		monthNames: [ "Januar", "Februar", "Mars", "April", 
		              "Mai", "Juni", "Juli", "August", 
		              "September", "Oktober", "November", "Desember"
		],
		prettyDate: function(date) {
			var y = date.getFullYear();
			var m = utils.monthNames[date.getMonth()];
			return m+" "+y;
		},

		
}
*/