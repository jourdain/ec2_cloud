girder.views.TaskView = girder.View.extend(
    _.extend({}, girder.mixins.vm(), girder.mixins.project, girder.mixins.task, {

    events: {
        'click .add-new-task': 'emptyTask',
        'click .save-new-task' : 'saveTask',
        'click .cancel-new-task' : 'cancelTask',
        'click .delete-task' : 'deleteTask',
        'click .g-task-selectable' : 'clickTask',
        'click .refresh-tasks': 'updateTasks'
    },

    initialize: function (settings) {
        this.setViewName('task');
        this.setDataDependency('project', 'task');

        this.collection = new girder.collections.TaskCollection();
        this.collection.on('g:changed', function () {
            console.log('render task because collection changed');
            this.invalidate();
            if(this.project) {
                console.log('fetch tasks for project ' + this.project.get('_id') + ' and got ' + this.collection.length);
            } else {
                console.log('no project');
            }
            this.trigger('g:changed');
        }, this);


        // Fetch collection when a project selected
        this.on('g:data:project', function(){
            if(this.project) {
                console.log('fetch tasks');
                this.collection.fetch({
                    parentType: 'folder',
                    parentId: this.project.get('_id'),
                }, true);
            }
        });
    },

    render: function () {
        if(this.project) {
            console.log('TaskView::render');
            this.$el.html(jade.templates.taskView({
                project: this.project,
                tasks: this.collection.models,
                placeholder: 'Filter tasks...',
                taskToEdit: this.task,
                girder: girder
            }));
        } else {
            console.log('TaskView::render - no project');
        }

        if(this.task) {
            console.log('TaskView::render - task');
            girder.vm.view('task-node-type').setSelection(this.task.get('node'));
            girder.events.trigger('g:view', 'task-node-type');

            girder.vm.view('task-action-type').setSelection(this.task.get('task'));
            girder.events.trigger('g:view', 'task-action-type');

            this.$('.g-task-title input').focus();
        } else {
            console.log('TaskView::render - no task');
        }
        return this;
    },

    emptyTask: function () {
        this.task = new girder.models.TaskModel();
        this.task.set({
            name: "",
            description: "",
            size: 1,
            created: new Date().toString(),
            status: 0
        });
        console.log('render task because emptyTask');
        this.invalidate();
    },

    saveTask: function () {
        // Extract task fields
        var fields = {},
            that = this;
        this.$('.task-field').each(function(){
            var me = $(this),
                key = me.attr('g-task-field'),
                value = me.val();

            fields[key] = value;
        });

        // Update task fields
        this.task.set(_.extend(fields, {
            parentType: 'folder',
            parentId: this.project.get('_id')
        }));

        // Save task
        var hasId = this.task.get('_id');
        this.task.off().on('g:error', function(err){
            girder.events.trigger('g:alert', err);
        }).on('g:saved', function(){
            if(!hasId) {
                that.collection.add(that.task);
            }

            // Render the new task list
            girder.events.trigger('g:data',{task: null});
            that.trigger('g:changed');
        }).save();
    },

    deleteTask: function () {
        var that = this;

        this.task.off().on('g:deleted', function(){
            that.collection.remove(that.task);
            girder.events.trigger('g:data',{task: null});
        }).on('g:error', function(err){
            girder.events.trigger('g:alert', err);
        }).destroy();
    },

    cancelTask: function () {
        girder.events.trigger('g:data',{task: null});
    },

    updateTasks: function() {
        console.log('update tasks');
        var that = this;
        if(this.project) {
            girder.restRequest({
                path: 'task/tasks/' + this.project.get('_id')
            }).done(function(){
                console.log('update tasks done');
                that.trigger('g:data:project', that.project);
            });
        }
    },

    clickTask: function(event) {
        var target = $(event.target),
            id = target.closest('.g-task-selectable').attr('g-task-id');
        if(target.hasClass('g-task-connect')) {
            console.log('connect to task');
        } else if(target.hasClass('g-task-start')) {
            console.log('start task ' + id);
            girder.restRequest({
                path: 'task/start/' + id,
                type: 'PUT'})
            .done(_.bind(function (resp) {
                if(this.project) {
                    console.log('fetch tasks');
                    this.collection.fetch({
                        parentType: 'folder',
                        parentId: this.project.get('_id'),
                    }, true);
                }
            }, this));
        } else {
            this.editTask(event);
        }
    },

    editTask: function(event) {
        var taskId = $(event.target).closest('.g-task-selectable').attr('g-task-id'),
            task = null;

        // Search item with matching id
        this.collection.each(function(item){
            if(item.get('id') === taskId) {
                task = item;
            } else if(item.get('_id') === taskId) {
                task = item;
            }
        });

        // Update active task
        girder.events.trigger('g:data',{task: task});
    }

}));

girder.router.route('project/:id/tasks', function (id) {
    // Fetch the project by id, then render the view.
    var project = new girder.models.FolderModel();
    project.set({
        _id: id
    }).on('g:fetched', function () {
        console.log('trigger g:view task (from taskView)');
        girder.events.trigger('g:data', { project: project });
        girder.events.trigger('g:view', 'task');
    }, this).on('g:error', function () {
        girder.router.navigate('/', {trigger: true});
    }, this).fetch();
});
