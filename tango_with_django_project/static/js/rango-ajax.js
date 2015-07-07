$(document).ready(function() {
//	Category likes
	$('#likes').click(function(){
		var catid;
		catid = $(this).attr("data-catid");
		$.get('/rango/like_category/', {category_id: catid}, function(data){
			$('#like_count').html(data);
			$('#likes').hide();
		});
	});

//	Refresh results but not the whole page
	$('#search').click(function(){
		var query;
		query = $('#query').val();
		$.get('/rango/category_search/', {query: query}, function(data){
			$('#search_results').html(data);
		});
	});

//	Category filter
	$('#suggestion').keyup(function(){
		var query;
		var dict;
		query = $(this).val();
		catid = $(this).attr("data-catid");
		if(catid.length != 0){
			$.get('/rango/suggest_category/', {suggestion: query, catid: catid}, function(data){
				$('#nav-sidebar').hide();
				$('#cats').html(data);
			});
		} else {
			$.get('/rango/suggest_category/', {suggestion: query, catid: ''}, function(data){
				$('#nav-sidebar').hide();
				$('#cats').html(data);
			});
		}
	});
});