define(function(require, exports, module) {
	var UI = require('js/alert');
	var $ = require('jquery');
	var DataTable= require('datatables');
	
    
	require('js/dataTables.semanticui.min');
	require('js/dataTables.colReorder.min');
	require('js/dataTables.buttons.min');
	require('js/jquery.serialize-object.min');
	
	$(function(){
		
		var t = $('#auctionDT').DataTable({
			"processing": true,
			"serverSide": false,
			"colReorder": true,
			"scroll":true,
			"scrollX": true,
			"scrollY": getheight(),
			"ajax":{
				"url": "/data/auction",
				"type": "POST",
				"data": function(d){
					d.op = "get";
				}
			},
			"columns":[
                {"data":null,
                    "orderable":false,
                    "searchable":false,
                    "width":10,
                    "defaultContent": '<div class="ui fitted checkbox"><input type="checkbox"> <label></label></div>',
                },
                {"data":null, "width":10,"orderable":false},
				{"data": "auctionid", "width":30, "name": "物品序号"},
				{"data": "auctionname", "width":150, "name": "物品名称" },
                {"data": "auctionprice", "width":150, "name": "物品价格"},
                {"data": "auctionnum", "width":150, "name": "物品数量"},
                {"data": "auctiondesc", "width":150, "name": "物品描述"},
            ],
			             
            "order":[[1,'asc']],
                        
            "columnDefs":[{
                    "targets": 1,
                    "render":function(data, type, row, meta){
                        return meta.settings._iDisplayStart + meta.row + 1;
                    }
                },
            ],
			
			"buttons":{
                "dom" : {
					"container" : {
						className : 'toolbar'
					},
					"button" : {
						className : 'ui tiny black button',
					},
				},
                "buttons":[
                    {
                        "text": '<i class="add icon"></i>添加',
                        "action":function(e, dt, node, config){
                            window.location = window.location.pathname + "/add" ;
                        }
                    },
                    {
                        "enabled":false,
                        "text": '<i class="edit icon"></i>编辑',
                        "action":function(e, dt, node, config){
                            window.location = window.location.pathname + "/edit?id=" + dt.row(".selected").data().id; 
                        }
                    },{
                        "enabled":false,
                        "text": '<i class="delete icon"></i>删除',
                        "action":function(e, dt, node, config){
                            var ids = [];
                            var selected = dt.rows(".selected").data();
                            if( !selected.length ) return;
                            $.each(selected, function(i,d){
                                ids.push(d.id);	
                            });	
                            UI.confirm({
                                header: "警告",
                                content: "确定要删除所选物品信息？",
                                actions:{
                                    yes:function(event){
                                        $.ajax({
                                            url: "/data/auction",
                                            async: false,
                                            type: "POST",
                                            dataType: "json",
                                            data:{
                                                op: "delete",
                                                ids: ids.join(",")
                                            },
                                            success:function(retData){
                                                if(retData.code){
                                                    UI.alert(retData.msg);
                                                }else{
                                                    UI.alert("删除成功！");
                                                    setTimeout(function(){
                                                        dt.ajax.reload();
                                                    },1000 );
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
                        "text": '<i class="refresh icon"></i>刷新',
                        "action": function(e,dt, node, config){
                            dt.ajax.reload();
                        }
                    },{
						"enabled":false,
						"text": '<i class="desktop icon"></i>详细信息',
						"action":function(e, dt, node, config){
							window.location =  "/data/auctionview/detail?id=" + dt.row(".selected").data().id;
						}
					}
                ],
            },
			
			
           	"dom": '<"ui autopadding grid"<"ten wide computer ten wide tablet sixteen wide mobile column"<"#toolbar">B><"six wide computer six wide tablet sixteen wide mobile right aligned column"f>>rt<"ui autopadding grid"<"six wide computer six wide tablet sixteen wide mobile column"i><"ten wide computer ten wide tablet sixteen wide mobile right aligned column"p>><"clear">',
			
			"initComplete": function ( settings, json ) {
				var dt = this.api();
				//dt.buttons([1,2,4]).disable();
			},
			
			"drawCallback":function(settings){
				var dataTables_wrapper = $(this).parents(".dataTables_wrapper");
				dataTables_wrapper.find(".dataTables_scrollHeadInner thead th").each(function(i,e){
					if(settings.aoColumns[i].name)
						$(e).html(settings.aoColumns[i].name)
				})
			},
			
			"headerCallback": function( thead, data, start, end, display ) {  //第一列第一个选框设置为全选
				$(thead).find('th').eq(0).html('<div class="ui fitted checkbox all"><input type="checkbox"> <label></label></div>');
			},
			
			
			
			
		});
		
		
		window.onresize = function(){
			$('.dataTables_scrollBody').css("height", getheight() + "px")
		};
		
		$(document).on('click', '#auctionDT tr',function(){
		    var $this = $(this),
			    $checkbox =$(this).find(".checkbox");
			if($this.hasClass("selected") ){
				if($checkbox.checkbox("is checked") )
					$checkbox.checkbox("uncheck");
			}else{
				if(!$checkbox.checkbox("is checked") )
					$checkbox.checkbox("check");
			};
			$this.toggleClass("selected");
			checkBtns();
			
		}).on('click', '.checkbox.all',function(){
		    var $this = $(this);
			if ($this.checkbox("is checked") ){
				$("#auctionDT tbody tr").addClass("selected")
										.find(".checkbox").checkbox("check");				
			}else{
				$("#auctionDT tbody tr").removeClass("selected")
										.find(".checkbox").checkbox("uncheck");
			};
			checkBtns();
				
		}).on("dblclick", "tr",function(){
		    window.location ="/data/auctionview/detail?id=" + $(this).closest("table").DataTable().row(this).data().id;	
		});
		
		
	});
	
	function getheight(){
		return $("#content").height() - 130;
	};
	function checkBtns(){
		var dt = $("#auctionDT").DataTable();
		var rows = dt.rows(".selected")[0];
		if(rows.length > 0){
			dt.buttons([2]).enable();
		}else{
			dt.buttons([2]).disable();
		};
		if (rows.length ==1){
			dt.buttons([1,4]).enable();
		}else{
			dt.buttons([1,4]).disable();
		};
		
	};
	
});