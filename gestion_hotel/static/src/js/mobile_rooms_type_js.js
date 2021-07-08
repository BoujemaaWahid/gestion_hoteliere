odoo.define('hotel_r.mobile_rooms_types_widget', function (require) {
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
        this.set({"art":this.recordData.types_rooms_for_mobile_text});
    },
    start: function() {
        var self = this;
        if (self.setting)
            return;

        if (! this.get("art") )
               return
        else{

        var data = this.get("art")
        data = data.split(",")
        console.log(data)
        this.set({"art":data})
        }
        this.renderElement();

     },
     initialize_field: function() {
         FormView.ReinitializeWidgetMixin.initialize_field.call(this);
         var self = this;
         self.on("change:art", self, self.start);
     },
     renderElement: function() {
         this._super();
         this.$el.html(QWeb.render("mobile_rooms_types", {widget: this}));
    },
    _onFieldChanged: function (event) {
    	this._super();
        this.lastChangeEvent = event;
        var data = this.recordData.types_rooms_for_mobile_text
        data = data.split(",")
    	this.set({"art": data});
        this.renderElement();
    },
});

registry.add(
    'mobile_widget_rt', MyWidget
);
return MyWidget
});