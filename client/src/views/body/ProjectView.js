/**
 * This view shows a single project
 */
girder.views.ProjectView = girder.View.extend(
    _.extend({}, girder.mixins.vm(), girder.mixins.project, {

    initialize: function() {
        this.setViewName('project');
        this.setSubViews('navigation');
        this.setDataDependency('project');
    },

    render: function () {
        if(this.project) {
            console.log('ProjectView::render');

            // Update content
            this.$el.html(jade.templates.projectView({
                project: this.project
            }));
        } else {
            console.log('ProjectView::render - no project');
        }

        return this;
    }
}));

girder.router.route('project/:id', function (id) {
    console.log('ProjectView route');

    // Fetch the project by id, then render the view.
    var project = new girder.models.FolderModel();
    project.set({
        _id: id
    }).on('g:fetched', function () {
        console.log('trigger g:view project (from projectView)');
        girder.events.trigger('g:data', { project: project });
        girder.events.trigger('g:view', 'project');
    }, this).on('g:error', function () {
        girder.router.navigate('/', {trigger: true});
    }, this).fetch();
});
