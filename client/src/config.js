// Register application views
girder.vm.register(new girder.views.NavigationBar(), '.g-header-wrapper');

girder.vm.register(new girder.views.NodeTypeWidget(), '.g-cluster-node-type-widget');
girder.vm.register(new girder.views.TaskTypeWidget(), '.g-task-type-widget');

girder.vm.register(new girder.views.ProjectsView(), '#g-app-body-container');
girder.vm.register(new girder.views.ProjectView(), '#g-app-body-container');
girder.vm.register(new girder.views.ClusterView(), '#g-app-body-container');
girder.vm.register(new girder.views.StorageView(), '#g-app-body-container');
girder.vm.register(new girder.views.TaskView(), '#g-app-body-container');
girder.vm.register(
    new girder.views.ProjectsToolbar({
        resultSelector: '#g-app-body-container',
        placeholder: 'Filter page...',
        fields: ['name', 'description'],
        selectors: ['.g-project-title', '.g-project-content'],
        projectView: 'projects'
    }),
    '.g-project-toolbar'
);


// Extend girder view with VM
girder.views.LayoutHeaderUserViewVM = girder.views.LayoutHeaderUserView.extend(
    _.extend({}, girder.mixins.vm(), {
        initialize: function () {
            this.setViewName('user');
        }
    })
);
girder.vm.register(new girder.views.LayoutHeaderUserViewVM(), '.g-current-user-wrapper');
