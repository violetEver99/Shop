define(function(require, exports, module) {
	var $ = require('jquery');
	var UI = require('js/alert');
	require("semantic");
	require('js/jquery.nicescroll.min');
	var DataTable = require('datatables');
	
	$(function(){
		$('#user .ui.dropdown').dropdown({
			action:"hide",
			onChange:function(value,text,$selectedItem){
				if(value == "1"){
					$("#changePass").modal("show");
					return;
				}else{
					window.location = "/logout";
					return;
				};
			}
		});
		$("#naviLeft").niceScroll();
		$(".niceScroll").niceScroll();
		$("#content").niceScroll({horizrailenabled: false});
		$("body").on("click","button.showNavi, button.hideNavi",function(){
			$("#naviLeft, #naviHide").toggle();
			$(".right_modify").toggleClass("fullScreen");
		});
		if($.fn.DataTable){
			$.extend( true, $.fn.DataTable.defaults, {
				"language": {
					"decimal":        "",
					"emptyTable":     "无数据",
					"info":           "当前显示 _START_ 到 _END_ 条，共 _TOTAL_ 条记录",
					"infoFiltered":   "(检索自 _MAX_ 条记录)",
					"infoEmpty":      "",
					"infoPostFix":    "",
					"thousands":      ",",
					"lengthMenu":     "每页显示 _MENU_ 条记录",
					"loadingRecords": "读取数据中...",
					"processing":     "加载中...",
					"search":         "搜索:",
					"zeroRecords":    "没有找到相关记录",
					"paginate": {
						"first":      "首页",
						"last":       "末页",
						"next":       "下一页",
						"previous":   "上一页"
					}
				 },
				"drawCallback":function(settings){
					$(this).find("thead th").each(function(i,e){
						if(settings.aoColumns[i].name)
							$(e).html(settings.aoColumns[i].name)
					})
				},
				
			} );
		};
		if($.fn.modal){
			var transition = ["horizontal flip","vertical flip","fade up","fade","scale"];
			$.extend( true, $.fn.modal.settings, {
				"observeChanges": true,  //for calendar ui
				"closable": false,
				"allowMultiple": true,
				"transition": transition[Math.floor(Math.random() * 5)],
				"onHidden": function(){
					if (this.id.indexOf("modal_box") == -1)
						$(this).modal("setting","transition",transition[Math.floor(Math.random() * 5)]);
					$(this).find("form").form("clear");
					//if ($(".dataTable:visible").length && this.id.indexOf("modal_box") == -1)
					//	$(".dataTable:visible").DataTable().ajax.reload();
					$(".myFileEvent").nextAll().remove();
					$(".myFileEvent").prev().val("");
				},
				"onShow": function(){
					$(".dimmer").niceScroll();
					$(this).removeClass("scrolling");
				}
			});
		};
		if($.fn.calendar){
			$.extend( true, $.fn.calendar.settings, {
				text: {
					days: ['日', '一', '二', '三', '四', '五', '六'],
					months: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'],
					monthsShort: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
					today: '今天',
					now: '现在',
				},
				ampm: false,
				formatter: {
					date: function (date, settings) {
						if (!date) return '';
						var day = date.getDate();
						var month = date.getMonth() + 1;
						var year = date.getFullYear();
						return year + '-' + month + '-' + day;
					}
				}
			});
		};
		/*$('.ui.modal').modal({
			closable:false,
			transition: "horizontal flip",
			onHidden:function(){
				var transition = ["horizontal flip","vertical flip","fade up","fade","scale"];
				$(this).modal("setting","transition",transition[Math.floor(Math.random() * 5)]);
				$(this).find("form").form("clear");
				$(".dataTable:visible").DataTable().ajax.reload();
			}
		});*/
		$(".menu a[href='/data/missionview']").append('<div class="ui red circular label tiny hidden missionNum" style="margin: -.5em 0;">0</div>');
		$(document).on("click",".menu a",function(e) {
			$(".ripple").remove();
			
			var $this = $(this),
				posX = $this.offset().left,
				posY = $this.offset().top,
				buttonWidth = $this.width(),
				buttonHeight = $this.height();
			 
			$this.prepend("<span class='ripple'></span>");
			 
			if (buttonWidth >= buttonHeight) {
				buttonHeight = buttonWidth;
			} else {
				buttonWidth = buttonHeight;
			}
			 
			var x = e.pageX - posX - buttonWidth / 2;
			var y = e.pageY - posY - buttonHeight / 2;
			 
			$(".ripple").css({
				width: buttonWidth,
				height: buttonHeight,
				top: y + 'px',
				left: x + 'px'
			}).addClass("rippleEffect");
		   
		}); 
		$("#changePass").modal({
			onApprove:function(){
				var passwd1 = $("#passwd1").val(),
					passwd2 = $("#passwd2").val();
				if( !passwd1 ){
					UI.alert("请输入新密码");
					return true;
				};
				if( passwd1 != passwd2 ){
					UI.alert("密码不一致");
					return true;
				};
				$.ajax({
					url: '/usermanage/changepw',
					async: false,
					type: "POST",
					dataType: "json",
					data: {
						"op": "self",
						"data": passwd1
					},
					success:function(retData){
						if (retData.code){
							UI.alert(retData.msg);
							return true;
						}else{
							UI.alert("修改密码成功");
							return false;
						};
					}
				});
			}
		});
		$("#pictureModal").modal({
			"closable":true
		});
		$(document).on("click", "a.afile", function(e){
			var href = $(this).attr("href");
			if( href.endsWith("png") || href.endsWith("gif") || href.endsWith("jpg") || href.endsWith("jpeg") || href.endsWith("bmp")){
				e.preventDefault();
				$("#pictureModal .header").html($(this).text());
				$("#pictureModal img").attr("src", href);
				$("#pictureModal").modal("show")
								  .css("top", "0px")
								  .css("margin-top", "0px");
			};
			
		}).on("click", ".bulk", function () {
			$("#bulkInput").modal("show");
			var uuid = new Date().getTime();
			$(this).parent().attr("id", uuid);
			$("#bulkInput").data("uuid", uuid);
		}).on("click", ".deleteText", function () {
			$(this).parent().remove();
		});
		
		$("#textInput").on("keydown",function (e) {
			var event = e ? e :(window.event ? window.event : null);
			var $this = $(this);
			if(event.keyCode==13 && $this.val()){
				var $tags = $this.parent().next();
				$this.val().split(",").map(function (d) {
					if( !!d )
						$tags.append('<div class="ui label small blue" data-value="' +  d + '">' + d + '<i class="delete icon deleteText"></i> </div>');
				});
				$this.val("");
			};
		});

		$("#fileInput").on("input propertychange", function () {
			var file = this.files[0],
				reader = new FileReader(),
				$tags = $(this).parent().next().next();
			reader.readAsText(file);
			reader.onload = function () {
				reader.result.split("\r\n").map(function (d) {
					if( !!d )
						$tags.append('<div class="ui label small blue" data-value="' +  d + '">' + d + '<i class="delete icon deleteText"></i> </div>');
				});
			};
		});
		$("#bulkInput").modal({
			onShow:function () {
				$(this).find(".labelArea").empty();
			},
			onApprove:function () {
				var $this = $(this),
					value = [],
					uuid = $this.data("uuid"),
					$origin = $("#" + uuid),
					$myList = $origin.find(".mylist"),
					isStruct = $origin.hasClass("structType"),
					$input = $origin.find("input:not(.ignore)"),
					data = $input.val() ? JSON.parse($input.val()) : [];
				$this.find(".labelArea").find(".label").each(function () {
					if( isStruct ){
						var split = $(this).data("value").split(":"),
							value = [{"key": "left", "value": split[0]}, {"key": "right", "value": split[1] ? split[1] : ""}],
							text = split.join(":");
					}else{
						var value = $(this).data("value"),
							text = value;
					};
					data.push(value);
					var $item = $myList.find(".template").clone(true).removeClass("template");
					$item.find("span")
						 .text( text )
						 .data("value", value)
						 .show();
					$item.find(".input").remove();
					$myList.append($item);
				});
				$input.val(JSON.stringify(data));
			}
		});
	});
	/*window.onload = function(){
		var transAct = ["fly ", "slide "],
			transPos = ["left", "right", "up", "down"];
		
		$('#contentSpace').transition(transAct[Math.floor(Math.random() * 2)] + transPos[Math.floor(Math.random() * 4)]);
	}*/
});