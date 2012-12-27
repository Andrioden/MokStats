// backgroundColor animation plugin
(function(d){d.each(["backgroundColor","borderBottomColor","borderLeftColor","borderRightColor","borderTopColor","color","outlineColor"],function(f,e){d.fx.step[e]=function(g){if(!g.colorInit){g.start=c(g.elem,e);g.end=b(g.end);g.colorInit=true}g.elem.style[e]="rgb("+[Math.max(Math.min(parseInt((g.pos*(g.end[0]-g.start[0]))+g.start[0]),255),0),Math.max(Math.min(parseInt((g.pos*(g.end[1]-g.start[1]))+g.start[1]),255),0),Math.max(Math.min(parseInt((g.pos*(g.end[2]-g.start[2]))+g.start[2]),255),0)].join(",")+")"}});function b(f){var e;if(f&&f.constructor==Array&&f.length==3){return f}if(e=/rgb\(\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*,\s*([0-9]{1,3})\s*\)/.exec(f)){return[parseInt(e[1]),parseInt(e[2]),parseInt(e[3])]}if(e=/rgb\(\s*([0-9]+(?:\.[0-9]+)?)\%\s*,\s*([0-9]+(?:\.[0-9]+)?)\%\s*,\s*([0-9]+(?:\.[0-9]+)?)\%\s*\)/.exec(f)){return[parseFloat(e[1])*2.55,parseFloat(e[2])*2.55,parseFloat(e[3])*2.55]}if(e=/#([a-fA-F0-9]{2})([a-fA-F0-9]{2})([a-fA-F0-9]{2})/.exec(f)){return[parseInt(e[1],16),parseInt(e[2],16),parseInt(e[3],16)]}if(e=/#([a-fA-F0-9])([a-fA-F0-9])([a-fA-F0-9])/.exec(f)){return[parseInt(e[1]+e[1],16),parseInt(e[2]+e[2],16),parseInt(e[3]+e[3],16)]}if(e=/rgba\(0, 0, 0, 0\)/.exec(f)){return a.transparent}return a[d.trim(f).toLowerCase()]}function c(g,e){var f;do{f=d.css(g,e);if(f!=""&&f!="transparent"||d.nodeName(g,"body")){break}e="backgroundColor"}while(g=g.parentNode);return b(f)}var a={aqua:[0,255,255],azure:[240,255,255],beige:[245,245,220],black:[0,0,0],blue:[0,0,255],brown:[165,42,42],cyan:[0,255,255],darkblue:[0,0,139],darkcyan:[0,139,139],darkgrey:[169,169,169],darkgreen:[0,100,0],darkkhaki:[189,183,107],darkmagenta:[139,0,139],darkolivegreen:[85,107,47],darkorange:[255,140,0],darkorchid:[153,50,204],darkred:[139,0,0],darksalmon:[233,150,122],darkviolet:[148,0,211],fuchsia:[255,0,255],gold:[255,215,0],green:[0,128,0],indigo:[75,0,130],khaki:[240,230,140],lightblue:[173,216,230],lightcyan:[224,255,255],lightgreen:[144,238,144],lightgrey:[211,211,211],lightpink:[255,182,193],lightyellow:[255,255,224],lime:[0,255,0],magenta:[255,0,255],maroon:[128,0,0],navy:[0,0,128],olive:[128,128,0],orange:[255,165,0],pink:[255,192,203],purple:[128,0,128],violet:[128,0,128],red:[255,0,0],silver:[192,192,192],white:[255,255,255],yellow:[255,255,0],transparent:[255,255,255]}})(jQuery);

/*
 * This javascript file contains several hacks and tweaks to the admin page for
 * adding a match. These hacks include:
 * - Adding a button to loading last player list via ajax.
 * - Trigger on keyup events to validate input and summarize row.
 * - Trigger on keyup events to possible fill in last players round sums.
 */
$(document).ready(function() {
	
	// input change animation function
	function changeAnimate(obj) {
		obj.animate({
			backgroundColor: "#E9E47F",
		}, 400, function() {
			obj.animate({backgroundColor: "white",}, 400);
		});
	}
	
	var playersTable = $('table').first();
	
	//Left float delete match button
	$('.deletelink-box').addClass("left");
	//Add a button that - by using ajax - loads the last games player list.
	var loadPlayersButton = $('<input type="button" class="left" value="Use last playerlist (no save)">');
	loadPlayersButton.on("click", function(){
		$.get('../../../../ajax_last_playerlist/', function(data) {
			$(data).each(function(i, id) {
				var playerRowCount = playersTable.find('select').size()-1;
				if (i > playerRowCount-1) $('.add-row').find('a')[0].click(); //New player row
				playersTable.find('select').eq(i).val(id);
			});
		},'json');
	});
	$('.submit-row').append(loadPlayersButton);
	
	/*
	 * Triggers on every keyup event triggered in the match round input fields.
	 */
	playersTable.on('keyup', 'input', function(event) {
		
		var targetEle = $(this);
		
		// Summarize the players score
		var playerRow = $(this).parents('tr');
		var total = 0;
		playerRow.find('input[type=text]').each(function(){
			var value = $(this).val();
			if (isNaN(value)) alert("Not a number");
			else if (value != "") {
				if ($(this).parent().is('.field-sum_grand, .field-sum_trumph')) {
					total -= parseInt(value);
				}
				else total += parseInt(value);
			}
		});
		playerRow.find('.field-total').find('p').text(total);
		
		// Automatically fill in remaining numbers if possible
		if (settings.getSetting("auto-calc") == "true") {
	
			var addedPlayersCount = playersTable.find('select').filter(function() {
		        return $(this).val() != "";
			}).size();
			
			var playerRowInputs = [];
			playersTable.find("select").each(function(i) {
				var roundInputs = $(this).parents('tr').find('input').slice('2');
				if (i < addedPlayersCount-1) { // Not last player row
					var roundInputsWithValCount = roundInputs.filter(function(){
						return $(this).val() != ""; 
					}).size();
					if (roundInputsWithValCount < 7) return false; // Stops loop
					else playerRowInputs.push(roundInputs);
				}
				else if (i == addedPlayersCount-1) { // Last player row
					// Summarize all other players sum together
					var roundSums = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0};
					$(playerRowInputs).each(function() { // Each player
						$(this).each(function(i) { // Each player's round value
							roundSums[i] += parseInt($(this).val());
						});
					});
					// Spades
					if (!roundInputs.eq(0).val() && !targetEle.is(roundInputs.eq(0))) {
						var spadesInPlay = $.inArray(addedPlayersCount,[6,8,9]) != -1 ? 12 : 13;
						roundInputs.eq(0).val(spadesInPlay-roundSums[0]);
						changeAnimate(roundInputs.eq(0));
					}
					// Queens
					if (!roundInputs.eq(1).val() && !targetEle.is(roundInputs.eq(1))) {
						roundInputs.eq(1).val(16-roundSums[1]);
						changeAnimate(roundInputs.eq(1));
					}
					// Pass|Grand|Trumph
					var cardsPerPlayer = Math.floor(52/addedPlayersCount);
					$([4,5,6]).each(function(_, i) {
						if (!roundInputs.eq(i).val() && !targetEle.is(roundInputs.eq(i))) {
							roundInputs.eq(i).val(cardsPerPlayer-roundSums[i]);
							changeAnimate(roundInputs.eq(i));
						}
					});
				}
			});
		}	
	});
	
	// Initiate settings
	settings.initSettingsBox();
});

var settings = new function() {
	var PREPEND = "setting.";
	
	this.getSetting = function(key) {
		return window.localStorage.getItem(PREPEND+key);
	};
	
	this.setSetting = function(key, val) {
		window.localStorage.setItem(PREPEND+key, val);
	};
	
	this.initSettingsBox = function() {
		var thisSettings = this;
		
		var cBox = $('<span class="setting_item left"><input type="checkbox"> Automatic Calculation</span>');
		if (this.getSetting("auto-calc") == "true") cBox.find('input').prop('checked', true);
		cBox.find('input').on("click", function() {
			var isChecked = $(this).prop('checked');
			thisSettings.setSetting("auto-calc", isChecked);
		});
		$('.submit-row').append(cBox);
	}
	
	
}