// Fill task mixin
girder.mixins.task = {
    task: null,

    setTask : function(v) {
        var changed = (this.task != v);
        this.task = v;
        if(changed) {
            this.trigger('g:data:task');
        }
    },

    getTask : function() {
        return this.task;
    }
}