girder.views.TaskTypeWidget = girder.View.extend(
    _.extend({}, girder.mixins.vm(), girder.mixins.project, girder.mixins.selection(), {

    events: {
        'change select': 'updateHidden'
    },

    initialize: function () {
        this.setViewName('task-action-type');
        this.setDataDependency('project');

        this.tasksType = [];
        this.taskMap = {}

        var that = this;
        $.getJSON( girder.staticRoot + "/templates/tasks.json", function( data ) {
            that.tasksType = data;
            _.each(data, function(task){
                that.taskMap[task.id] = task;
            });
        });
    },

    render: function () {
        if(this.project) {
            console.log('TaskTypeWidget::render');
            this.$el.html(jade.templates.taskTypeWidget({
                project: this.project,
                tasks: this.tasksType,
                active: this.selection
            }));
            this.updateHidden();
        } else {
            console.log('TaskTypeWidget::render - no project');
        }

        return this;
    },

    updateHidden: function () {
        var id = this.$('select').val(),
            hiddenValue = this.$('input[name="web"]');

        if(this.taskMap.hasOwnProperty(id)) {
            hiddenValue.val(this.taskMap[id].endpoint.length ? 1 : 0);
        }
    }
}));