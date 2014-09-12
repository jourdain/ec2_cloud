// Fill project mixin
girder.mixins.vm = function() {
    return {
        name: null,
        subViews: [],
        dataDependency: [],

        setViewName : function(name) {
            this.name = name;
        },

        setSubViews : function() {
            var that = this;
            this.subViews = [];
            _.each(arguments, function(item) {
                that.subViews.push(item);
            });
        },

        setDataDependency : function() {
            var that = this;
            this.dataDependency = [];
            _.each(arguments, function(item) {
                that.dataDependency.push(item);
            });
        },

        getName : function() {
            return this.name;
        },

        getSubViews : function() {
            return this.subViews;
        },

        getDataDependency : function() {
            return this.dataDependency;
        },

        invalidate : function() {
            girder.vm.invalidate(this.name);
        }
    };
}