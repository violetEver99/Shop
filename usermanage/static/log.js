define(function(require, exports, module) {
	var UI = require('js/alert');
	var $ = require('jquery');
	var dataTable= require('datatables');
	
	
	require('js/dataTables.semanticui.min');
	require('js/dataTables.buttons.min');
	require('js/jquery.serialize-object.min');

	$(function(){
		
		/*var checkenable = function(){
			if($('#example').DataTable().rows('.selected').data().length == 1){
				$('#example').DataTable().buttons($('#example').DataTable().buttons()[1].node).enable();	
			}else{
				$('#example').DataTable().buttons($('#example').DataTable().buttons()[1].node).disable();
			};
			if($('#example').DataTable().rows('.selected').data().length > 0){
				$('#example').DataTable().buttons($('#example').DataTable().buttons()[2].node).enable();	
			}else{
				$('#example').DataTable().buttons($('#example').DataTable().buttons()[2].node).disable();
			};
		};*/
 	    var t = $('#example').dataTable( {
			/*"processing": true,
			"serverSide": true,
			"ajax": {
				"url": "/case/GetCaseItems",
				"type": "POST"
			},*/
			"autoWidth":false,
			"data": [
				{"id":"", "type":"审核", "user":"admin", "date":"2016年9月8日 15:34:30", "op":"通过了用户<b>test</b>提交的单位信息"},
				{"id":"", "type":"提交", "user":"test", "date":"2016年9月8日 10:20:30", "op":"提交了单位信息<b>xx测试单位信息</b>"},
				{"id":"", "type":"全文检索", "user":"test", "date":"2016年9月7日 17:32:30", "op":"全文检索，关键词为<b>线索1</b>"},
				{"id":"", "type":"用户管理", "user":"admin", "date":"2016年9月7日 16:30:30", "op":"新建用户 <b>test</b> "},
			],
			"columns": [
/* 				{"data":null,
				"orderable":  false,
				"searchable": false,
				"width":40,
				"defaultContent": '<div class="ui fitted checkbox"><input type="checkbox"> <label></label></div>',
				
				}, */
				{ "data": "type", "width":"10%"},
				{ "data": "user", "width":"10%"},
				{ "data": "date", "width":"20%"},
				{ "data": "op",},

			],
			"order": [[1, 'asc']],
			"dom": '<<"six wide computer six wide tablet sixteen wide mobile right aligned column"f>>rt<"ui autopadding grid"<"six wide computer six wide tablet sixteen wide mobile column"l><"ten wide computer ten wide tablet sixteen wide mobile right aligned column"p>><"clear">',
			/*"buttons": {
				"dom" : {
					"container" : {
						className : 'toolbar'
					},
					"button" : {
						className : 'ui tiny black button',
					},
				},
				"buttons": [
					{
						"text": '<i class="add icon"></i>新建',
						"titleAttr" : '新建用户',
						"action": function ( dt ) {
							$('#adduser').modal('show');
						}
					},{
						"text": '<i class="edit icon"></i>编辑',
						"titleAttr" : '编辑',
						"action": function ( dt ) {
							var selected = $('#userTable').DataTable().rows('.selected').data()[0];
							$('#editusername').val(selected.username);
							$('#edituserid').val(selected.id);
							$('#editrole').val(selected.roleid);
							$('#editdepartment').val(selected.department);
							$('#editinfo').val(selected.info);
							//$('#edituser .ui.dropdown').dropdown("set active",selected.roleid);
							$('#edituser .ui.dropdown').dropdown("set value",selected.roleid);
							$('#edituser .ui.dropdown').dropdown("set text",selected.role);
							$('#edituser').modal('show');
						}
					},					
					{
						"text": '<i class="remove icon"></i>删除',
						"titleAttr" : '删除',
						"action": function ( dt ) {
							UI.confirm({
								header:"警告",
								content:"确定要删除这些用户？",
								actions:{
									yes:function(event){
										var ids = [];
										var selected = $('#userTable').DataTable().rows('.selected').data();
										for (var i=0; i< selected.length; i++){
											ids.push(selected[i].id);
										};
										$.ajax({
											url: "/usermanage/delusers",
											async: false,
											type: "POST",
											//dataType: "json",
											data: {
												groupid:currentGroupId,
												ids:JSON.stringify(ids)
											},
											success:function(retdata){
												if(retdata == '0'){
													UI.alert("删除成功！");
													$('#userTable').DataTable().ajax.reload();
												}else{
													UI.alert("网络异常！");
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
					},
					{
						"text": '<i class="refresh icon"></i>刷新',
						"action": function () {
							var table = $('#example').DataTable();
							table.ajax.reload();
							$("#example thead .checkbox").checkbox("uncheck");
						}
					}
				]
			},*/
			//select: true,
			"drawCallback":function(settings, json){
				$("#toolbar").append('<i class="ace-icon fa fa-copy bigger-110 pink"></i>');

				/*$("#example tbody .checkbox").checkbox({
					fireOnInit : true,
					onChecked:function(){
						if(!$(this).closest('tr').hasClass('selected')){
							$(this).closest('tr').addClass('selected');
						}
						checkenable();

					},
					onUnchecked:function(){
						if($(this).closest('tr').hasClass('selected')){
							$(this).closest('tr').removeClass('selected');
						}
						checkenable();

					},
					/*onChange:function(){
						var $checkbox = $("table tbody .checkbox"); 
						$checkbox.each(function() {
							if( $(this).checkbox('is checked') ) {
								if(!$(this).closest('tr').hasClass('selected')){
									$(this).closest('tr').addClass('selected');
								}
							}
							else {
								if($(this).closest('tr').hasClass('selected')){
									$(this).closest('tr').removeClass('selected');
								}
							  
							}
						  });
					}*/
				/*});*/
				$("#example thead .checkbox").checkbox({
					fireOnInit : true,
					onChecked:function(){
						var $childCheckbox  = $("#example tbody .checkbox");
						$childCheckbox.checkbox('check');
					},
					onUnchecked:function(){
						var $childCheckbox  = $("#example tbody .checkbox");
						$childCheckbox.checkbox('uncheck');
					}
				});
			},
			"initComplete": function () {
				var api = this.api();
				api.$('tr').dblclick( function () {
					var rowdata = $('#example').DataTable().rows(this).data()[0];
					$("#casename").val(rowdata.casename);
					$("#casetype").val(rowdata.casetype);
					$("#caseindex").val(rowdata.caseindex);
					$("#casestatus").val(rowdata.casestatus);
					$("#createdate").val(rowdata.createdate);
					$("#info").val(rowdata.info);
					$("#caseid").val(rowdata.caseid);
					$('#caseModal > .header').html("编辑案件");
					$('#caseModal').modal('show');
				} );
			}
			
		}); 
		$(document).on("click",".dtdetail",function(){
			/*var rowdata = $('#example').DataTable().rows($(this).parents("tr")).data()[0];
			var modal = rowdata.type == "新建" ? "#newModal" : "#editModal";
			$(modal + " #submituser").text(rowdata.owner);
			$(modal + " #submittime").text(rowdata.time);
			$(modal + " #checktime").text(rowdata.checktime);
			$(modal + " #submitresult").text(rowdata.status);
			$(modal + " #opiniondiv").show();
			if(rowdata.status == "已通过"){
				$(modal + " #status").removeClass("active disabled").addClass("completed");
				$(modal + " #opiniondiv").removeClass("red").addClass("green");
			}else if(rowdata.status == "不通过"){
				$(modal + " #status").removeClass("active completed").addClass("disabled");
				$(modal + " #opiniondiv").removeClass("green").addClass("red");
			}else{
				$(modal + " #status").removeClass("disabled completed").addClass("active");
				$(modal + " #opiniondiv").hide();
			};
			$(modal).modal('show');*/
			
		});	
		
	
		
		

		$('#caseModal').modal({
			closable:true,
			transition:"horizontal flip",
			onApprove:function(e){
				//
				if($('#caseModal .ui.form').form("is valid")){
					$('#caseModal .ui.form .submit.button').api("query");
				};
				return false;
			}
		});
		$('#newModal').modal({
			closable:true,
			transition:"horizontal flip",
		});
		$('#editModal').modal({
			closable:true,
			transition:"horizontal flip",
		});
		
		$('#caseModal .ui.form').form({
			fields: {
			  casename: {
				identifier: 'casename',
				rules: [
				  {
					type   : 'empty',
					prompt : '请输入案件名称！'
				  }
				]
			  },
			  casetype: {
				identifier: 'casetype',
				rules: [
				  {
					type   : 'empty',
					prompt : '请选择案件类型'
				  }
				]
			  },
			  caseindex: {
				identifier: 'caseindex',
				rules: [
				  {
					type   : 'empty',
					prompt : 'Please select a gender'
				  }
				]
			  },
			  casestatus: {
				identifier: 'casestatus',
				rules: [
				  {
					type   : 'empty',
					prompt : 'Please enter a username'
				  }
				]
			  },
			  createdate: {
				identifier: 'createdate',
				rules: [
				  {
					type   : 'empty',
					prompt : 'Please enter a password'
				  },
				  {
					type   : 'minLength[6]',
					prompt : 'Your password must be at least {ruleValue} characters'
				  }
				]
			  },
			  terms: {
				identifier: 'terms',
				rules: [
				  {
					type   : 'checked',
					prompt : 'You must agree to the terms and conditions'
				  }
				]
			  }
			},
			"inline": true,
			"on": 'submit',
			"onSuccess":function(){
				
				
			}
		  });
		
		// stop the form from submitting normally 
		$('#caseModal .ui.form').submit(function(e){ 
			//e.preventDefault(); usually use this, but below works best here.
			//$("#caseModal div[type='submit']").trigger('click');
			
			return false;
		});
		
		$('#caseModal .ui.form .submit.button').api({
			url: '/case/EditCaseItem',
			method : 'POST',
			serializeForm: true,
			dataType:'text',
			data: {
				caseid: 1
			},
			beforeSend: function(settings) {
				settings.data.userID = 1; 
				return settings;
			},
			onResponse: function(response) {
				// make some adjustments to response
				//console.log(response);
				return response;
			},
			onError: function(errorMessage) {
				alert(errorMessage);
			},
			onFailure:function(response){
				alert(1);
				
			},
			onSuccess: function(data) {
				//alert(data);
				return false;
			}
		});


    });
	

	
});