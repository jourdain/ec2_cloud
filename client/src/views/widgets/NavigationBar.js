girder.views.NavigationBar = girder.View.extend(
    _.extend({}, girder.mixins.vm(), girder.mixins.project, {

    events: {
        'click .clickable' : function(e) {
            girder.router.navigate( $(e.target).attr('href'), {trigger: true});
        }
    },

    initialize: function () {
        this.setViewName('navigation');
        this.setSubViews('user');
        this.setDataDependency('project');

        this.on('g:data:project', function() {
            this.invalidate();
        });
    },

    render: function () {
        var id = null,
            title = 'Cloud HPC';

        if(this.project) {
            id = this.project.get('_id');
            title = this.project.get('name');
        }

        this.$el.html(jade.templates.navigationBar({
            title: title,
            id: id
        }));

        return this;
    }
}));
