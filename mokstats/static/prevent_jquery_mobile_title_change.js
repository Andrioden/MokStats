// jquery mobile sets the visible page title, this line of code rewrite that to the correct title. 
// Which is the one specified in <head>
$(":jqmData(role='page')").attr("data-title", document.title);