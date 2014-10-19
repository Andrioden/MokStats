// jquery mobile sets the visible page title, this line of code rewrite that to the correct
$(":jqmData(role='page')").attr("data-title", document.title);