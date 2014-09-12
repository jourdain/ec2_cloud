/**
 * This widget provides a text field that will filter a given array of objects.
 */
girder.views.ProjectsToolbar = girder.View.extend(
    _.extend({}, girder.mixins.vm(), {

    events: {
        'input .g-filter-field': '_doFilter',
        'click .add-project': 'createProjectDialog',
        'click .remove-project': 'deleteProjetcs'
    },

    initialize: function (settings) {
        this.setViewName('projects-toolbar');

        this.placeholder = settings.placeholder || 'Search...';
        this.fields = settings.fields || [ 'name' ];
        this.resultSelector = settings.resultSelector;
        this.selectors = settings.selectors;
        this.projectView = settings.projectView;

        this.resultContainer = null;
    },

    render: function () {
        console.log('ProjectsToolbar::render');
        this.$el.html(jade.templates.projectsToolbar({
            placeholder: this.placeholder
        }));

        this._doFilter();

        return this;
    },

    clearText: function () {
        this.$('.g-filter-field').val('');
        return this;
    },

    _doFilter: function () {
        var props = this.fields,
            containerToFilter = this.resultContainer,
            selects = this.selectors,
            query = this.$('.g-filter-field').val();

        if(!containerToFilter) {
            containerToFilter = this.resultContainer = $(this.resultSelector);
        }

        if(query) {
            query = query.toLowerCase();
            $('.g-project-entry', containerToFilter).hide().each(function(){
                var me = $(this),
                    count = selects.length;

                while(count--) {
                    if($(selects[count], me).html().toLowerCase().indexOf(query) !== -1) {
                        me.show();
                        count = 0;
                    }
                }
            });
        }
    },

    createProjectDialog: function () {
        new girder.views.EditFolderWidget({
            el: $('#g-dialog-container'),
            parentModel: girder.currentUser
        }).on('g:saved', function (folder) {
            girder.vm.view(this.projectView).insertProject(folder);
        }, this).render();
    },

    deleteProjetcs: function() {
        var actionButton = $('.remove-project'),
            parentView = girder.vm.view(this.projectView);
        if(actionButton.toggleClass('validate-delete').hasClass('validate-delete')) {
            // Allow project selection
            $('.g-project-delete').show();
            $('.g-project-entry').removeClass('go-to-project');
        } else {
            $('.g-project-entry').addClass('go-to-project');
            $('.g-project-delete').hide();

            // Delete selected projects
            var idToDelete = [];
            $('.g-project-block.g-selected').each(function(){
                var me = $(this),
                    id = me.parent().attr('g-project-id');
                idToDelete.push(id);
            });

            _.each(idToDelete, function(id) {
                girder.restRequest({path: '/folder/'+id, type: 'DELETE', success: function() {
                    parentView.removeProject(id);
                }})
            });

            console.log('delete the following: ' + idToDelete.join(', '));
        }

    }

}));
