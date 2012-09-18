function sortBy(type) {
	$('#players li').tsort("."+type, {order:'desc'})
}

function slashedRelativeHref(relativePath) {
	var path = window.location.pathname;
	if (path.charAt(path.length-1) != "/") path += "/";
	window.location.href=path+relativePath;
}