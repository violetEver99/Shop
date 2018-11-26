define(function(require,exports,module){
    var UI = require('js/alert');
	var $ = require('jquery');
	$(function(){
	    var data = JSON.parse($("#data").val());	
		$.each(data,function(key,value){
		    if (!value) return;
			var $span = $("#" + key);
			$span.html(value);
		});
	});
	
});