// Fill project mixin
girder.mixins.user = {
    user: null,

    setUser : function(v) {
        var changed = (this.user != v);
        this.user = v;
        if(changed) {
            this.trigger('g:data:user');
        }
    },

    getUser : function() {
        return this.user;
    }
}