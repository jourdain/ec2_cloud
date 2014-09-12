girder.views.StorageView = girder.View.extend(
    _.extend({}, girder.mixins.vm(), girder.mixins.project, {

    initialize: function() {
        this.setViewName('storage');
        this.setDataDependency('project');
    },

    render: function () {
        if(this.project) {
            console.log('StorageView::render');
            this.$el.html(jade.templates.storageView({
                project: this.project
            }));
        } else {
            console.log('StorageView::render - no project');
        }

        return this;
    }
}));

girder.router.route('project/:id/storages', function (id) {
    // Fetch the project by id, then render the view.
    var project = new girder.models.FolderModel();
    project.set({
        _id: id
    }).on('g:fetched', function () {
        console.log('trigger g:view storage (from storageView)');
        girder.events.trigger('g:data', { project: project });
        girder.events.trigger('g:view', 'storage');
    }, this).on('g:error', function () {
        girder.router.navigate('/', {trigger: true});
    }, this).fetch();
});
