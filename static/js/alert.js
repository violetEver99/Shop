define(function (require, exports, module) {

	require("semantic");
	var $ = require('jquery');
	var _ = require('js/lodash');
   var Modal = function (options) {
      this.options = {
         prefix: 'modal_box_',
         namespace: 'semantic-modal',
         closable: true,
         cls: null,
         // default message
         icon: '',
         header: '',
         content: '',
         actions: {}
      };
      if (_.isObject(options))
         _.merge(this.options, options);
      this.id = _.uniqueId(this.options.prefix);
      this.body = false;
      this.modal = false;
      this.buttons = {};
      this.bodyActionsBox = null;
   };

   Modal.prototype.hasBody = function () {
      if (this.body !== false)
         return true;
      var el = document.getElementById(this.id);
      if (el) {
         this.body = $(el);
         return true;
      }
      return false;
   };

   Modal.prototype.initBody = function () {
      if ($('#' + this.id).get(0))
         return this;
      var closeIcon = !!this.options.closable ? '<i class="close icon"></i>' : '';
      this.body = $('<div id="' + this.id + '" class="ui modal">' + closeIcon + '<div class="header"><i class="icon ' + this.options.icon + '"></i><span class="inner">' + this.options.header + '</span></div><div class="content">' + this.options.content +'</div></div>');
      this.body.modal(this.options);
      if (this.options.cls)
         this.body.addClass(this.options.cls);
      this.initActions(this.options.actions);
      // 先在内存中把整个modal初始化完成了，这样可以不用牺牲页面渲染的性能
      $('body').append(this.body);
      return this;
   };

   Modal.prototype.getBody = function () {
      if (!this.hasBody())
         this.initBody();
      return this.body;
   };

   Modal.prototype.getModal = function () {
      if (!this.modal) {
         this.modal = this.getBody().data('module-' + this.options.namespace);
      }
      return this.modal;
   };

   Modal.prototype.hasActions = function () {
      return !!this.bodyActionsBox;
   };

   Modal.prototype.removeActions = function () {
      if (this.bodyActionsBox) {
         this.bodyActionsBox.remove();
         this.bodyActionsBox = false;
      }
      return this;
   };

   Modal.prototype.initActions = function (actions) {
      if (_.size(actions) <= 0)
         return this.removeActions();
      var me = this;
      this.bodyActionsBox = $('<div class="actions"></div>');
      _.forOwn(actions, function (action, key) {
         me.initAction(key, action);
      });
	  if ( !!this.body.find(".actions").length )
		  this.body.find(".actions").remove();
      this.body.append(this.bodyActionsBox);
      return this;
   };

   Modal.prototype.initAction = function (name, action) {
      action = _.merge({
         text: null,
         cls: null,
         icon: null,
         click: null
      }, action || {});
      var me = this
         , text = action.text
         , icon = action.icon
         , cls = action.cls || '';
      if (!_.isString(text) || text === '')
         text = name;
      if (_.isString(icon) && icon !== '') {
         cls += ' icon labeled';
         text += '<i class="icon ' + icon + '"></i>';
      }
      var button = this.buttons[name] = $('<button type="button" class="ui button ' + cls + '">' + text + '</button>');
      button.prop('action', name);
      button.click(function () {
         me.action(button.prop('action'));
      });
      me.on(name, action.click);
      this.bodyActionsBox.append(button);
      return this;
   };

   Modal.prototype.on = function (event, fn, isOne) {
      var me = this, $me = $(this), handle = !!isOne ? $me.one : $me.on;
      if (_.isString(event)) {
         if (_.isFunction(fn))
            handle.call($me, event, fn);
         else if (_.isArray(fn) && fn.length > 0) {
            _.each(fn, function (item) {
               me.on(event, item, isOne);
            });
         }
      }
      else if (_.isObject(event)) {
         _.forOwn(event, function (value, name) {
            me.on(name, value, isOne);
         });
      }
      return this;
   };

   Modal.prototype.one = function (event, fn) {
      return this.on(event, fn, true);
   };

   Modal.prototype.action = function (name) {
      var isBreak = $(this).triggerHandler(name);
      if (isBreak !== false)
         this.hide();
      return this;
   };

   Modal.prototype.isShow = function () {
      return this.getModal().is.active();
   };

   Modal.prototype.isHide = function () {
      return !this.isShow();
   };

   Modal.prototype.show = function (message) {
      if (_.isFunction(message))
         message = {then: message};
      else if (typeof message !== 'undefined' && (_.isString(message) || _.isObject(message)))
         this.setMessage(message);
      if (this.isHide())
         this.getModal().showModal(message && message.then);
      return this;
   };

   Modal.prototype.hide = function (then, keepDimmer) {
      var me = this;
      if (this.isShow()) {
         this.getModal().hideModal(then, keepDimmer);
      }
      return this;
   };

   Modal.prototype.setMessage = function (message) {
      if (_.isString(message))
         message = {content: message};
      this.setIcon(message.icon || null);
      this.setHeader(message.header || null);
      this.setContent(message.content || null);
      this.setButton(message.button || null);
      if (message.actions)
         this.on(message.actions, null, true);
      return this;
   };
   Modal.prototype.setButton = function (button) {
	  var _this = this;
	  if (_.isObject(button)){
		 _.forOwn(button, function(val,key){
			 _.forOwn(val, function(val2,key2){
				if(key2=="cls")
					_this.options.actions[key][key2] += " " + val2;
				else
					_this.options.actions[key][key2] = val2;
			 });
		 });
		 this.initActions(this.options.actions);
	  };
   };
   Modal.prototype.setIcon = function (icon) {
      var item = this.getBody().find('.header .icon');
      if (!icon || icon == '')
         icon = this.options.icon;
      if (!icon || icon == '')
         item.css('display', 'none');
      else {
         item.css('display', '');
         item.addClass(icon);
      }
      return this;
   };

   Modal.prototype.setHeader = function (content) {
      var item = this.getBody().find('.header .inner');
      if (!content || content.length == '')
         content = this.options.header;
      item.html(content);
      return this;
   };

   Modal.prototype.setContent = function (content) {
      var item = this.getBody().find('.content');
      if (!content || content.length == '')
         content = this.options.content;
      item.html(content);
      return this;
   };

   var globalModals = {};

   var stdModalOptions = [
      {
         access: 'alert',
         closable: false,
		 allowMultiple: true,
         cls: 'small',
         icon: 'comment outline',
         header: '消息提示',
         actions: {
            'ok': {
               text: '好的',
               cls: 'green right',
               icon: 'checkmark'
            }
         }
      },
      {
         access: 'confirm',
         closable: false,
		 allowMultiple: true,
         cls: 'small',
         icon: 'warning',
         header: '请确认',
         content: '你确定吗？',
         actions: {
            'yes': {
               text: '确定',
               cls: 'green',
               icon: 'checkmark'
            },
            'no': {
               text: '取消',
               cls: 'red',
               icon: 'remove'
            }
         }
      }
   ];

   var exports = {};

   exports.ModalClass = Modal;

   var getModal = exports.modal = function (id, options) {
      if (!globalModals[id])
         globalModals[id] = new Modal(options);
      return globalModals[id];
   };

   _.each(stdModalOptions, function(options) {
      var name = options.access;
      exports[name] = function (message, show) {
         var modal = getModal(name, options).setMessage(message);
         if (typeof show === 'undefined')
            show = true;
         if (!!show)
            modal.show(show);
         return modal;
      }
   });

   return exports;
});