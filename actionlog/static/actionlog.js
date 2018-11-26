define(function(require, exports, module) {
	var UI = require('js/alert');
	var $ = require('jquery');
	var dataTable= require('datatables');
	var searchcolumn = "ALL";
	var canDelete = 1;  // 1 or 0 
	require('js/dataTables.semanticui.min');
	require('js/dataTables.buttons.min');
	require('js/jquery.serialize-object.min');

	$(function(){
		var columns = [
				{ "data": "id", "width":30, "name": "编号"},
				{ "data": "username","orderable": true,"width":80, "name": "操作用户"},
				{ "data": "ipaddr", "orderable": true, "width":80, "name": "使用IP地址"},
				{ "data": "action_time", "orderable": true, "width":120, "name": "操作时间"},
				{ "data": "action", "orderable": true, "width":300, "name": "操作内容"},

			];
		if( canDelete ){
			var buttonslist = [{
						"text": '<i class="remove icon"></i>删除',
						"titleAttr" : '删除',
						"action": function ( e, dt ) {
							UI.confirm({
								header:"警告",
								content:"确定要删除所选记录？",
								actions:{
									yes:function(event){
										var ids = [];
										var selected = dt.rows('.selected').data();
										$.each(selected,function(i,d){
											ids.push(d.id);
										});
										$.ajax({
											url: "/actionlog/log",
											async: false,
											type: "POST",
											dataType: "json",
											data: {
												op:"delete",
												ids:ids.join(",")
											},
											success:function(retData){
												if(retData.code){
													UI.alert(retData.msg);
												}else{
													UI.alert("删除成功！");
													dt.ajax.reload();
												};
											}
										});
									},
									no:function(event){
										return true;
									}
								}
							});
						}
					}
			];
			columns.unshift({
				"data":null,
				"orderable":  false,
				"searchable": false,
				"width":22,
				"defaultContent": '<div class="ui fitted checkbox"><input type="checkbox"> <label></label></div>',
				});
			
		}else{
			var buttonslist = [];
			
		};
 	    var t = $('#logDT').dataTable( {
			"processing": true,
			"serverSide": true,
			"ajax": {
				"url": "/actionlog/log",
				"type": "POST",
				"data": function(d) {
					return $.extend( {}, d, {
						"searchcolumn": $("input#mycolumn").val() ? $("input#mycolumn").val() : "ALL",
						"op": "get"
					});
                },
			},
			"columns": columns,
			"order": [[canDelete, 'asc']],
			"dom": '<"ui autopadding grid"<"eight wide computer sixteen wide tablet sixteen wide mobile column"<"#toolbar">B><"eight wide computer sixteen wide tablet sixteen wide mobile right aligned column"<"mydataTableDropdown ui dropdown selection">f>>rt<"ui autopadding grid"<"six wide computer sixteen wide tablet sixteen wide mobile column"i><"ten wide computer sixteen wide tablet sixteen wide mobile right aligned column"p>><"clear">',
			"buttons": {
				"dom" : {
					"container" : {
						className : 'toolbar'
					},
					"button" : {
						className : 'ui tiny black button',
					},
				},
				"buttons": buttonslist,
			},
			//select: true,
			"initComplete": function () {
				var $mydataTableDropdown = $(".ui.mydataTableDropdown");
				$mydataTableDropdown.append($("<input id='mycolumn' name='column' type='hidden' value='ALL'></input>\
												<i class='dropdown icon'></i>\
												<div class='default text'>全部</div>\
												<div class='menu'>\
													<div class='item' data-value='ALL'>全部</div>\
													<div class='item' data-value='username'>用户名</div>\
													<div class='item' data-value='ipaddr'>IP地址</div>\
												  </div>"));
				$mydataTableDropdown.dropdown({
					onChange:function(value,text,$choice){
						searchcolumn = value;	
						$('#logDT').DataTable().ajax.reload();
					}
				});
			},
			"headerCallback": function( thead, data, start, end, display ) {
				if(canDelete){
					$(thead).find('th').eq(0).html( '<div class="ui fitted checkbox"><input type="checkbox"> <label></label></div>' );
					checkBtns();
				}
			},
		}); 
		
		$(document).on("click","thead .checkbox",function(){
			var _this = $(this);
			$(this).closest('table').find("tbody tr").each(function(i,e){
				if(_this.checkbox("is checked")){
					$(e).addClass('selected');
					$(e).find(".checkbox").checkbox("check");
				}else{
					$(e).removeClass('selected');
					$(e).find(".checkbox").checkbox("uncheck");
				};
			});
			checkBtns();
		});
		$(document).on("click","tbody .checkbox",function(){
			$(this).closest('tr').toggleClass('selected');
			checkBtns();
		});

		$(document).on('dblclick', 'td', function () {
			var dt = $(this).closest("table").DataTable();
			var value = dt.cell(this).data(),
				key = dt.column(this).dataSrc();
			if( key == "ipaddr" || key == "username" ){
				var keyName = {"ipaddr": "IP地址", "username": "用户名"};
				$(".ui.mydataTableDropdown").dropdown("set value", key);
				$(".ui.mydataTableDropdown").dropdown("set text", keyName[key]);
				dt.search(value);
				dt.ajax.reload();
			}
		});
    });
	function checkBtns(){
		if(canDelete){
			var dt = $('#logDT').DataTable();
			var rows = dt.rows(".selected")[0];
			if (rows.length > 0){
				dt.buttons([0]).enable();
			}else{
				dt.buttons([0]).disable();
			};
		};
	};
});