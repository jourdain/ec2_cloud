girder.views.NodeTypeWidget = girder.View.extend(
    _.extend({}, girder.mixins.vm(), girder.mixins.project, girder.mixins.selection(), {

    events: {
        'change select': 'updateHelp'
    },

    initialize: function () {
        this.setViewName('task-node-type');
        this.setDataDependency('project');

        this.nodeInfo = {};

        var that = this;
        $.getJSON( girder.staticRoot + "/templates/computers.json", function( data ) {
            that.nodeInfo = data;
        });
    },

    render: function () {
        if(this.project) {
            console.log('NodeTypeWidget::render');
            this.$el.html(jade.templates.nodeTypeWidget({
                project: this.project,
                computers: this.nodeInfo,
                active: this.selection
            }));
            this.updateHelp();
        } else {
            console.log('NodeTypeWidget::render - no project');
        }

        return this;
    },

    updateHelp: function () {
        var id = this.$('select').val();
        this.$('.help').addClass('hidden');
        this.$('.help[help-id="ID"]'.replace(/ID/g, id)).removeClass('hidden');
    }
}));