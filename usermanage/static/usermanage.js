define(function(require, exports, module) {
	var UI = require('js/alert');
	var $ = require('jquery');
	var newCount =1;
	var currentGroupId = $('#basegroupid').val();
	var baseGroupId = $('#basegroupid').val();
	var DataTable= require('datatables');
	var mtree = null;
	var menutree = null;
	var datatree = null;
	
	
	require('js/dataTables.semanticui.min');
	require('js/dataTables.buttons.min');
	require('js/jquery.serialize-object.min');
	require('js/jquery.ztree.all.min');
	
	
	function addHoverDom(treeId, treeNode) {
		var sObj = $("#" + treeNode.tId + "_span");
		if (treeNode.editNameFlag || $("#addBtn_"+treeNode.tId).length>0) return;
		var addStr = "<span class='button add' id='addBtn_" + treeNode.tId
			+ "' title='add node' onfocus='this.blur();'></span>";
		sObj.after(addStr);
		var btn = $("#addBtn_"+treeNode.tId);
		if (btn) btn.bind("click", function(){
			var zTree = $.fn.zTree.getZTreeObj("mtree");
			zTree.addNodes(treeNode, {id:(100 + newCount), pId:treeNode.id, name:"new node" + (newCount++)});
			return false;
		});
	};
	
	function removeHoverDom(treeId, treeNode) {
		$("#addBtn_"+treeNode.tId).unbind().remove();
	};
	
	// zTree configuration information, refer to API documentation (setting details)
	var setting = {"check":{"enable": true,"chkboxType":{"Y" : "ps", "N" : "ps"}},
					"edit":{"drag":{"autoExpandTrigger":true,"isCopy":true,},"enable": false,
		"editNameSelectAll": true,"showRenameBtn": true,
		"renameTitle": "编辑节点名称","showRemoveBtn": true,},
					//"view":{"addHoverDom": addHoverDom,"removeHoverDom": removeHoverDom,"selectedMulti": false}
	};

	// zTree data attributes, refer to the API documentation (treeNode data details)
	/*var zNodes = [
		{name:"归口1", open:true, children:[
			{name:"test1_1"}, 
			{name:"test1_2"}]
			},
		{name:"归口2", open:true, children:[
			{name:"test2_1"}, {name:"test2_2"}]
			},
		{name:"归口3", open:true, children:[
			{name:"test2_1"}, {name:"test2_2"}]
			},
		{name:"归口4", open:true, children:[
			{name:"test2_1"}, {name:"test2_2"}]
			}
		];
		
		
	function buildtree(gid){
		$.ajax({
			url: "/usermanage/getdeptree",
			async: false,
			type: "POST",
			//dataType: "json",
			data: {
				groupid:gid
			},
			success:function(retData){
				if(retData != ""){
					var depNodes = JSON.parse(retData);
					if(mtree != null) mtree.destroy();
					mtree = $.fn.zTree.init($("#mtree"), {
						callback: {
							onClick:function(event, treeId, treeNode){
								//alert(treeNode.id);
								currentGroupId = treeNode.id;
								$("#_group").text(treeNode.name);
								$('#userDT').DataTable().ajax.reload();
								$('#groupDT').DataTable().ajax.reload();
								buildMenuTree(currentGroupId);
							} 
					}}, depNodes);

				}else{
					UI.alert("网络异常！");
				};
			}
		});
	}*/
		
	function buildMenuTree(gid){	
		$.ajax({
			url: "/usermanage/getmenu",
			async: false,
			type: "GET",
			dataType: "json",

			success:function(retData){
				if(retData.code){
					UI.alert(retData.msg);
				}else{
					if(menutree != null) menutree.destroy();
					menutree = $.fn.zTree.init($("#menutree"), setting, retData);
				};
			}
		});		
	};
		
	function travCheckboxs(permsDir){
		var nodes = menutree.transformToArray(menutree.getNodes());
		$.each(nodes,function(i,d){
			var permID = d.id;
			if(permID in permsDir){
				menutree.checkNode(d, true, false);
			}else{
				menutree.checkNode(d, false, false);
			}
		});
	};
	
	var checkBtns = function(){
		var type = $(".ui.tab.active").data("tab");
		var dt = $('.ui.tab.active table').DataTable();
		var rows = dt.rows(".selected")[0];
		if (rows.length > 0){
			dt.buttons([2]).enable();
		}else{
			dt.buttons([2]).disable();
		};
		if (rows.length == 1){
			dt.buttons([1]).enable();
			if(type == "group")
				dt.buttons([3]).enable();
		}else{
			dt.buttons([1]).disable();
			if(type == "group")
				dt.buttons([3]).disable();
		};
	};
	
	
	$(function(){
		$(".ui.selection.dropdown").dropdown();
		//var zTreeObj = $.fn.zTree.init($("#mtree"), setting, zNodes);
		buildMenuTree();
		//buildtree(baseGroupId);
		$('#contentTab .menu .item').tab();
		$('#permTab .menu .item').tab();

		
		$('.ui.dropdown.group').dropdown({
			apiSettings: {
				url: '/usermanage/group',
				method : 'POST',
 				/*data:{
					op:"get",
					flag:0
				}, */
				on: 'click',
				cache: false,
				beforeSend: function(settings) {
					settings.data.op = "get";
					settings.data.flag = 0;
					settings.data.key = $(this).find("input.search").val();
					return settings;
				},
				/*onResponse: function(response) {
					JSON.stringify(response);
					return response;
				},*/
			
			},
			saveRemoteData: false,
			
		});
		
		$('#addGroup .ui.dropdown').dropdown();
		$('#edigroup .ui.dropdown').dropdown();
		
		
		var t = $('#userDT').DataTable( {
			"processing": true,
			"serverSide": false,
			//"autoWidth": false,
			"ajax": {
				"url": "/usermanage/user",
				"type": "POST",
				"data": function(d) {
					d.op = "get";
                },
			},
			"columns": [
				{"data":null,
				 "orderable": false,
				 "searchable": false,
				 "width": 10,
				"defaultContent": '<div class="ui fitted checkbox"><input type="checkbox"> <label></label></div>',
				
				},
				{ "data": "username", "name": "用户名"},
				{ "data": "role","orderable": false, "name": "角色"},
				{ "data": "department","orderable": false, "name": "部门"},
				{ "data": "info","width":"42%","orderable": false, "name": "备注"},
				/*
				{
					"data": null,
					"orderable":  false,
					"defaultContent": "<button>Click!</button>"
				}*/
			],
			"order": [[1, 'asc']],
			"buttons": {
				"dom" : {
					"container" : {
						"className" : 'toolbar'
					},
					"button" : {
						"className" : 'ui tiny black button',
					},
				},
				"buttons": [
					{
						"text": '<i class="add icon"></i>新建',
						"titleAttr" : '新建用户',
						"action": function ( e, dt, node, config ) {
							$('#addUser').modal('show');
						}
					},{
						"enabled": false,
						"text": '<i class="edit icon"></i>编辑',
						"titleAttr" : '编辑',
						"action": function ( e, dt, node, config ) {
							var data = dt.rows('.selected').data()[0];
							$('#editUser .ui.form').form('set values',data);
							$('#editUser .ui.dropdown').dropdown("set text",data.role);
							$('#editUser .ui.dropdown').dropdown("set value",data.roleid);
							$('#editUser').modal('show');
						}
					},					
					{
						"enabled": false,
						"text": '<i class="remove icon"></i>删除',
						"titleAttr" : '删除',
						"action": function ( e, dt, node, config ) {
							UI.confirm({
								header:"警告",
								content:"确定要删除这些用户？",
								actions:{
									yes:function(event){
										var ids = [];
										var selected = $('#userDT').DataTable().rows('.selected').data();
										for (var i=0; i< selected.length; i++){
											ids.push(selected[i].userid);
										};
										$.ajax({
											url: "/usermanage/user",
											async: false,
											type: "POST",
											dataType: "json",
											data: {
												op:"del",
												ids:JSON.stringify(ids)
											},
											success:function(retData){
												if(retData.code){
													UI.alert(retData.msg);
												}else{
													UI.alert("删除成功");
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
					}, {
						"text": '<i class="refresh icon"></i>刷新',
						"action": function ( e, dt, node, config ) {
							dt.ajax.reload();
							dt.buttons([1,2]).disable();
						}
					}
				]
			},
			"dom": '<"ui autopadding grid"<"ten wide computer ten wide tablet sixteen wide mobile column"<"#toolbar">B><"six wide computer six wide tablet sixteen wide mobile right aligned column"f>>rt<"ui autopadding grid"<"six wide computer six wide tablet sixteen wide mobile column"i><"ten wide computer ten wide tablet sixteen wide mobile right aligned column"p>><"clear">',
			//select: true,
			"headerCallback": function( thead, data, start, end, display ) {
				$(thead).find('th').eq(0).html( '<div class="ui fitted checkbox"><input type="checkbox"> <label></label></div>' );
				checkBtns();
			},
		}); 
		
		var t1 = $('#groupDT').DataTable( {
			"processing": true,
			"serverSide": false,
			"autoWidth": false,
			"ajax": {
				"url": "/usermanage/group",
				"type": "POST",
				"data": function(d) {
					d.op = "get";
                },
			},
			"columns": [
				{"data":null,
				 "orderable": false,
				 "searchable": false,
				 "width":"23px",
				"defaultContent": '<div class="ui fitted checkbox"><input type="checkbox"> <label></label></div>',
				
				},
				{ "data": "groupname", "name": "角色名"},
				{ "data": "city", "name": "地市"},
				{ "data": "usable", "name": "状态"},
				{ "data": "info","width":"45%","orderable": false, "name": "备注"},
				/*{
					"data": null,
					"orderable":  false,
					"defaultContent": "<button>Click!</button>"
				}*/
			],
			"order": [[1, 'desc']],
			"dom": '<"ui autopadding grid"<"ten wide computer ten wide tablet sixteen wide mobile column"<"#toolbar">B><"six wide computer six wide tablet sixteen wide mobile right aligned column"f>>rt<"ui autopadding grid"<"six wide computer six wide tablet sixteen wide mobile column"i><"ten wide computer ten wide tablet sixteen wide mobile right aligned column"p>><"clear">',
			"buttons": {
				"dom" : {
					"container" : {
						"className" : 'toolbar'
					},
					"button" : {
						"className" : 'ui tiny black button',
					},
				},
				"buttons": [
					{
						"text": '<i class="add icon"></i>新建',
						"titleAttr" : '新建角色',
						"action": function ( e, dt, node, config ) {
							$('#addGroup').modal('show');
						}
					},{
						"enabled": false,
						"text": '<i class="edit icon"></i>编辑',
						"titleAttr" : '编辑',
						"action": function (e, dt, node, config) {
							var data = dt.rows('.selected').data()[0];
							$('#editGroup .ui.form').form('set values',data);

							$('#editGroup').modal('show');
							
							
						}
					},{
						"enabled": false,
						"text": '<i class="remove icon"></i>删除',
						"titleAttr" : '删除',
						"action": function ( e, dt, node, config ) {
							UI.confirm({
								header:"警告",
								content:"确定要删除这些用户组？属于这些用户组的用户也将被删除！",
								actions:{
									yes:function(event){
										var ids = [];
										var selected = $('#groupDT').DataTable().rows('.selected').data();
										for (var i=0; i< selected.length; i++){
											ids.push(selected[i].id);
										};
										$.ajax({
											url: "/usermanage/group",
											async: false,
											type: "POST",
											//dataType: "json",
											data: {
												op:"del",
												ids:JSON.stringify(ids)
											},
											success:function(retData){
												if(retData.code){
													UI.alert(retData.msg);
												}else{
													UI.alert("删除成功");
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
					},{
						"enabled": false,
						"text": '<i class="bug icon"></i>权限',
						"titleAttr" : '权限',
						"className" : 'pusherbtn',
						"action": function ( e, dt, node, config ) {			
							var data = dt.row('.selected').data();
							$.ajax({
								url: "/usermanage/perms",
								async: false,
								type: "POST",
								dataType: "json",
								data: {
									id: data.id,
									op: "get",
									type: "menu"
								},
								success:function(retData){
									travCheckboxs(retData);
								}
							});
							$('#userPerms').modal('show');
							var name = data.groupname;
							$("#userPerms span#_user").text(name);

						}
					},{
						"text": '<i class="refresh icon"></i>刷新',
						"action": function ( e, dt, node, config ) {
							dt.ajax.reload();
							dt.buttons([1,2,3]).disable();
						}
					}
				]
			},
			//select: true,
			"headerCallback": function( thead, data, start, end, display ) {
				$(thead).find('th').eq(0).html( '<div class="ui fitted checkbox"><input type="checkbox"> <label></label></div>' );
				checkBtns();
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


		
		$('#userDT').on('dblclick','tbody tr',function(){
			var data = $(this).closest("table").DataTable().row(this).data();
			$('#editUser .ui.form').form('set values',data);
			$('#editUser .ui.dropdown').dropdown("set text",data.role);
			$('#editUser .ui.dropdown').dropdown("set value",data.roleid);
			$('#editUser').modal('show');
		}); 
		$('#groupDT').on('dblclick','tbody tr',function(){
			var data = $(this).closest("table").DataTable().row(this).data();
			$('#editGroup .ui.form').form('set values',data);
			$('#editGroup').modal('show');
		}); 
		
		
		$('#addUser').modal({
			onApprove:function(e){
				if($('#addUser .ui.form').form("is valid"))
					$('#addUser .submit.button').api('query');
				return false;
			}
		});
		
		$('#editUser').modal({
			onApprove:function(e){
				if($('#editUser .ui.form').form("is valid"))
					$('#editUser .submit.button').api('query');
				return false;
			}
		});
		
		$('#addGroup').modal({
			onApprove:function(e){
				if($('#addGroup .ui.form').form("is valid"))
					$('#addGroup .submit.button').api('query');
				return false;
			}
		});
		
		$('#editGroup').modal({
			onApprove:function(e){
				if($('#editGroup .ui.form').form("is valid"))
					$('#editGroup .submit.button').api('query');
				return false;
			}
		});

		$('#userPerms').modal({
			onApprove:function(e){
				var permsType = $(this).find(".tab.active").data("tab");
				var perms;
				if (permsType == "direction"){
					perms = $(this).find("input#direction").val();
				}else if(permsType == "city"){
					perms = $(this).find("span.default").text() + "," + $(this).find("input#city").val();
				}else{
					var permsList = menutree.getCheckedNodes(true).map(item => item.id);
					perms = JSON.stringify(permsList);
				};
				var gid = $('#groupDT').DataTable().row('.selected').data().id;
				$.ajax({
					url: "/usermanage/perms",
					async: false,
					type: "POST",
					dataType: "json",
					data: {
						op:"set",
						id:gid,
						perms:perms,
						type:permsType
					},
					success:function(retData){
						if(retData.code){
							UI.alert(retData.msg);
						}else{
							UI.alert("成功修改用户权限！");
							$("#permTab .item").tab("change tab",$("#permTab .tab.active").data("tab"));
						};
					}
				});
				return false;
			},
			onHide:function(){
				$("#permTab .item").tab("change tab","menu");
			}
		});
		
		$("#permTab .item").tab({
			"onLoad": function(tabPath){
				var data = $('#groupDT').DataTable().row('.selected').data();
				if (tabPath == "direction" || tabPath == "city"){
					$.ajax({
						url: "/usermanage/perms",
						async: false,
						type: "POST",
						//dataType: "json",
						data: {
							id: data.id,
							op: "get",
							type: tabPath
						},
						dataType: "json",
						success:function(retData){
							if(retData){
								$("#permTab .tab.active span.value").data("data",retData);
								$("#permTab .tab.active span.value").html(retData.join(","));
								$(".showEdit").show();
								$("#permTab .tab.active .ui.dropdown").hide();
							};
						}
					});
					
				};
				if (tabPath == "city"){
					$("span.default").html(data.city);
				};
			}
		});
		$(".showEdit i").on("click",function(){
			$(this).parent().hide();
			$(this).parent().next().show();
			var datas = $(this).prev().data("data");
			var $dropdown = $(this).parent().next();
			$dropdown.click();
			setTimeout(function(){
				$dropdown.dropdown("refresh");
				$dropdown.dropdown("set exactly", datas);
			},500);
		});
		
		$('.ui.form.user').form({
			"fields" : {
				name: {
					identifier: 'username',
					rules: [
						{
							type   : 'empty',
							prompt : '用户名不能为空'
						},{
							type   : 'doesntContain[_]',
							prompt : '用户名不能含有“_”'
						}
					]
				},
				role: {
					identifier: 'role',
					rules: [
						{
							type   : 'empty',
							prompt : '请为选择一个角色,若无可选角色请在【角色】中新建角色并分配权限！'
						}
					]
				},
				password: {
					identifier: 'passwd',
					rules: [
						{
							type   : 'minLength[6]',
							prompt : '密码至少为6位'
						}
					]
				}
			},
			"inline": true,
			"on": 'submit'
		});
		
		$('.ui.form.group').form({
			"fields" : {
				groupname: {
					identifier: 'groupname',
					rules: [
						{
							type   : 'empty',
							prompt : '名称不能为空'
						}
					]
				},
				city: {
					identifier: 'city',
					rules: [
						{
							type   : 'empty',
							prompt : '请选择地市'
						}
					]
				},
				

			},
			"inline": true,
			"on": 'submit'
		});
		
		// stop the form from submitting normally 
		$('.ui.form').submit(function(e){ 
			//e.preventDefault(); usually use this, but below works best here.
			return false;
		});
		
		$('#addUser .submit.button').api({
			url: '/usermanage/user',
			method : 'POST',
			serializeForm: true,
			dataType:'json',
			beforeSend: function(settings) {
				settings.data.op = "add";
				return settings;
			},

			onSuccess: function(retData) {
				if(retData.code){
					UI.alert(retData.msg);
				}else{
					UI.alert("成功创建新用户！");
					$('#addUser').modal('hide');
					$("#userDT").DataTable().ajax.reload();
				};
			}
		});
		
		$('#editUser .submit.button').api({
			url: '/usermanage/user',
			method : 'POST',
			serializeForm: true,
			dataType:'json',
/* 			data: {
				groupid:currentGroupId,
			}, */
			beforeSend: function(settings) {
				settings.data.op = "edit";
				return settings;
			},

			onSuccess: function(retData) {
				if(retData.code){
					UI.alert(retData.msg);
				}else{
					UI.alert("成功修改用户信息！");
					$('#editUser').modal('hide');
					$("#userDT").DataTable().ajax.reload();
				};
			}
		});
		
		
		$('#addGroup .submit.button').api({
			url: '/usermanage/group',
			method : 'POST',
			serializeForm: true,
			dataType:'json',
			beforeSend: function(settings) {
				settings.data.op = "add";
				return settings;
			},
			onSuccess: function(retData) {
				if(retData.code){
					UI.alert(retData.msg);
				}else{
					UI.alert("成功创建新用户组！");
					$('#addGroup').modal('hide');
					$("#groupDT").DataTable().ajax.reload();
				};
			}
		});
		
		
		$('#editGroup .submit.button').api({
			url: '/usermanage/group',
			method : 'POST',
			serializeForm: true,
			dataType:'json',
			beforeSend: function(settings) {
				settings.data.op = "edit";
				return settings;
			},
			onSuccess: function(retData) {
				if(retData.code){
					UI.alert(retData.msg);
				}else{
					UI.alert("成功修改用户组信息！");
					$('#editGroup').modal('hide');
					$("#groupDT").DataTable().ajax.reload();
				};
			}
		});
		
		/*$("#userPerms .folder.icon").on("dblclick",function(){
			$(this).next().find("div.list").toggle();
			$(this).toggleClass("open");
		});
		
		$("#userPerms .checkbox").checkbox({
			onChecked:function(){
				$($(this).parents(".item")[1]).children().checkbox("check");
			}
		});*/
		$(".ui.dropdown.editDirection").dropdown({
			apiSettings: {
				url: '/data/clue',
				method : 'POST',
				cache: false,
				beforeSend: function(settings) {
					settings.data.op = "getattr";
					settings.data.flag = 0;
					settings.data.type = "direction";
					settings.data.key = $(this).find("input.search").val();
					return settings;
				},
				onResponse:function(response){
					response.results.pop();
					return response;
				}				
			},
			on: 'click',
			/*action: function(text,value){
				if(value=="new"){
					$(this).next().transition("fade right");
				}else{
					$(this).dropdown("set selected", value);
					$(this).next().transition("hide");
				}
			},*/
			
			saveRemoteData: false,
			
		});
		$(".changepw").on("click",function(){
			$.ajax({
				url: '/usermanage/changepw',
				async: false,
				type: "POST",
				dataType: "json",
				data: {
					"op": "reset",
					"id": $("#edituserid").val()
				},
				success:function(retData){
					if (retData.code){
						UI.alert(retData.msg);
						return true;
					}else{
						UI.alert("成功重置密码为“888888”");
						return false;
					};
				}
			});
		});
	});
});