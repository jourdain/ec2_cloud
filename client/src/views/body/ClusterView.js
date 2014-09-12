girder.views.ClusterView = girder.View.extend(
    _.extend({}, girder.mixins.vm(), girder.mixins.project, {

    events: {
        'click .g-cluster-delete' : function(event) {
            var entry = $(event.target).closest('.g-cluster-container'),
                id = entry.attr('g-cluster-id'),
                that = this;
            girder.restRequest({
                path: 'task/cluster/' + id,
                type: 'DELETE'
            }).done(function(){
                console.log("Kill cluster");
                that.trigger("g:data:project");
            });
        },
        'click .refresh' : 'updateClusters'
    },

    initialize: function() {
        var that = this;
        this.setViewName('cluster');
        this.setDataDependency('project');
        this.clusters = [];
        this.on('g:data:project', function(){
            that.updateClusters();
        });
    },

    render: function () {
        if(this.project) {
            console.log('cluster render');
            this.$el.html(jade.templates.clusterView({
                project: this.project,
                clusters: this.clusters
            }));
        } else {
            console.log('cluster render - no project');
        }
        return this;
    },

    updateClusters: function(){
        var that = this;
        this.clusters = [];
        if(this.project) {
            girder.restRequest({
                path: 'task/clusters/' + this.project.get('_id')
            }).done(function(clusters){
                that.clusters = clusters;
                that.invalidate();
            });
        }
    }
}));

girder.router.route('project/:id/clusters', function (id) {
    // Fetch the project by id, then render the view.
    var project = new girder.models.FolderModel();
    project.set({
        _id: id
    }).on('g:fetched', function () {
        console.log('trigger g:view cluster (from clusterView)');
        girder.events.trigger('g:data', { project: project });
        girder.events.trigger('g:view', 'cluster');
    }, this).on('g:error', function () {
        girder.router.navigate('/', {trigger: true});
    }, this).fetch();
});
