odoo.define('hotel_r.hotel_ca_clients', function (require) {
'use strict';

var core = require('web.core');
var registry = require('web.field_registry');
var _t = core._t;
var basicFields = require('web.basic_fields');

var FieldText = basicFields.FieldText;
var InputField = basicFields.InputField;
var QWeb = core.qweb;

var MyWidget = FieldText.extend({
    events: _.extend({}, FieldText.prototype.events, {
        'change': '_onFieldChanged',
    }),
	init: function () {
    	this._super.apply(this, arguments);
    	if (this.mode === 'edit') {
            this.tagName = 'span';
        }
        this.set({"parent": py.eval(this.recordData.parent)});
    },
    start: function() {
        var self = this;
        if (self.setting)
            return;

        if (! this.get("parent") )
               return

        this.renderElement();

     },
     initialize_field: function() {
         FormView.ReinitializeWidgetMixin.initialize_field.call(this);
         var self = this;
         self.on("change:parent", self, self.start);
     },
     renderElement: function() {
         this._super();
         this.$el.html(QWeb.render("hotel_ca_h", {widget: this}));
    },
    _onFieldChanged: function (event) {
    	this._super();
        this.lastChangeEvent = event;
    	this.set({"parent": py.eval(this.recordData.parent)});
        this.renderElement();
    },
});

registry.add(
    'h_ca_clients', MyWidget
);
return MyWidget
});