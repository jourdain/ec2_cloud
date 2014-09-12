/**
 * This is the view for the front page of the app.
 */
girder.views.ProjectsView = girder.View.extend(
    _.extend({}, girder.mixins.vm(), girder.mixins.user, {

    events: {
        'click .g-project-entry' : function(event) {
            var entry = $(event.target).closest('.g-project-entry'),
                id = entry.attr('g-project-id');
            if(entry.hasClass('go-to-project')) {
                console.log('go to project ' + id);
                girder.router.navigate('project/' + id, {trigger: true});
            } else {
                entry.children().toggleClass('g-selected');
            }
        },
        'click .g-my-account-link': function () {
            girder.router.navigate('useraccount/' + girder.currentUser.get('_id') +
                                   '/info', {trigger: true});
        },
        'click .g-project-delete' : function(e) {
            $(e.target).parent().parent().toggleClass('g-selected');
        }
    },

    initialize: function () {
        this.setViewName('projects');
        this.setSubViews('navigation', 'projects-toolbar');
        this.setDataDependency('user');

        console.log('ProjectsView init');
        this.collection = new girder.collections.FolderCollection();
        this.collection.append = true; // Append, don't replace pages
        this.collection.on('g:changed', function () {
            this.invalidate();
            this.trigger('g:changed');
        }, this)


        this.on('g:data:user', function(){
            this.collection.fetch({
                parentType: 'user',
                parentId: this.user.get('_id')
            });
        });
    },

    render: function () {
        console.log('ProjectsView::render');

        this.$el.html(jade.templates.projectsView({
            apiRoot: girder.apiRoot,
            staticRoot: girder.staticRoot,
            currentUser: girder.currentUser,
            projects: this.collection.models,
            girder: girder
        }));

        return this;
    },

    insertProject: function(project) {
        this.collection.add(project);
        this.trigger('g:changed');
        this.invalidate();
    },

    removeProject: function(id) {
        var collection = this.collection,
            cidToDelete = null;

        // Search item with matching id
        collection.each(function(item){
            if(item.get('id') === id) {
                cidToDelete = item.cid;
            } else if(item.get('_id') === id) {
                cidToDelete = item.cid;
            }
        });

        // delete item
        if(cidToDelete) {
            collection.remove(cidToDelete);
            this.trigger('g:changed');
        }
        this.invalidate();
    }
}));

girder.router.route('projects', function () {
    if(girder.currentUser) {
        console.log('trigger g:view projects (from projectsView)');
        girder.events.trigger('g:data', { project: null , task: null});
        girder.events.trigger('g:view', 'projects');
    } else {
        girder.events.trigger('g:login');
    }
});
