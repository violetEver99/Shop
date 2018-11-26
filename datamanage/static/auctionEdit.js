define(function(require, exports, module){
	var UI = require('js/alert');
	var $ = require('jquery');
	require('js/calender');
	
	$(function(){
        $(".myform").form("clear");
		
		if($("#op").val() == "edit" ){
			var data = JSON.parse($("#data").val());
			if( !!data.code ){
				UI.alert(data.msg);
				$("#contentSpace").hide();
				return;
				//setTimeout(function(){
					//window.location = "/data/auctionview";
				//},3000 )
			};
			$.each(data,function(key,value){
				if(!value) return;
				var $input = $("[name='"+key+"']")
			    $input.val(value);
			});
				
			
		}
		
		$(".submit").on("click",function(){
			
		    $('.myform').form("validate form");
			if(!$('.myform').form("is valid"))
				return false;
			
			var fd = new FormData();
			var i=1;
			$("#contentSpace form").serializeArray().map(function(d,i){
				if(d.name != "ignore")
					fd.append(d.name,d.value);
			});
			if($("#op").val() == "add" ){
			    fd.append("op","add");
			}else{
				fd.append("op","edit");
				fd.append("_id",$("#id").val());
			};
			$.ajax({
				url: '/data/auction',
				async: false,
				type: "POST",
				dataType: "json",
				data: fd,
				processData: false,  
				contentType: false,   
				success:function(retData){
					if (retData.code){
						UI.alert(retData.msg);
						return false;
					}else{
						if($("#op").val() == "edit"){
							UI.alert("编辑成功，即将返回物品列表")
							setTimeout(function(){
								window.location = "/data/auctionview"
							},3000 );
						}else{
							UI.confirm({
								header:"提示",
								content:"添加成功，是否继续添加？",
								button:{
									yes:{
										"text":"继续添加",
										"cls":"myclass"
									},
									no:{
										"text":"返回物品列表"
									}
								},
								actions:{
									yes:function(event){
										window.location.reload(true);
									},
									no:function(event){
										window.location = "/data/auctionview";
									}
								}
							});
						};	
					};
				}
			});
			
		});
		
		$('.myform').form({
			fields: {
				auctionid: {
					identifier: 'auctionid',
					rules: [{
						type   : 'empty',
						prompt : '请输入序号！'
					}]
				},
				auctionname: {
					identifier: 'auctionname',
					rules: [{
						type   : 'empty',
						prompt : '请输入名称！'
					}]
				},
				auctionprice: {
					identifier: 'auctionprice',
					rules: [{
						type   : 'empty',
						prompt : '请输入价格！'
					}]
				},
				auctionnum: {
					identifier: 'auctionnum',
					rules: [{
						type   : 'empty',
						prompt : '请输入数量！'
					}]
				},
				auctiondesc:{
					identifier: 'auctiondesc',
					rules: [{
						type   : 'empty',
						prompt : '请输入物品描述！'
					}]
				},
				
			},
			"inline": true,
			"on": 'submit',
			"keyboardShortcuts": false,
			"onSuccess":function(){},
			"onFailure": function(formErrors, fields){
				$(".field.error").find("input").focus();
			}
		});
		
		
		
		
	
	});
	
});