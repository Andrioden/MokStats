$(document).ready(function() {
	// Find the correct table containing players and their results
	var playersTable = $('table').first();
	console.log(playersTable)
	// Update the total sum field on every user key input
	playersTable.on('keyup', 'input', function(event) {
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
	});
});