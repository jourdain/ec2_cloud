// Fill project mixin
girder.mixins.selection = function(){
    return {
        selection: '',

        setSelection : function(v) {
            this.selection = v;
        },

        getSelection : function() {
            return this.selection;
        }
    };
}