function sortBy(type) {
	$('#players li').tsort("."+type, {order:'desc'})
}