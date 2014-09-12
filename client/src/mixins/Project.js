// Fill project mixin
girder.mixins.project = {
    project: null,

    setProject : function(v) {
        if(this.project !== v) {
            if( (this.project === null || v === null)
                || (this.project !== null && v !== null && this.project.get('_id') !== v.get('_id'))) {
                this.project = v;
                this.trigger('g:data:project');
            }
        }
    },

    getProject : function() {
        return this.project;
    }
}