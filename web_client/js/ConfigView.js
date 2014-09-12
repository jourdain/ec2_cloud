/**
 * Administrative configuration view. Shows the global-level settings for this
 * plugin for all of the supported ec2_cloud providers.
 */
girder.views.ec2_cloud_ConfigView = girder.View.extend({
    events: {
        'submit #g-ec2_cloud-provider-starcluster-form': function (event) {
            event.preventDefault();
            this.$('#g-ec2_cloud-provider-starcluster-error-message').empty();

            this._saveSettings([{
                key: 'ec2_cloud.work.dir',
                value: this.$('#g-ec2_cloud-provider-startcluster-work-dir').val().trim()
            }, {
                key: 'ec2_cloud.template.config',
                value: this.$('#g-ec2_cloud-provider-starcluster-template-file').val().trim()
            }]);
        }
    },
    initialize: function () {
        girder.restRequest({
            type: 'GET',
            path: 'system/setting',
            data: {
              list: JSON.stringify(['ec2_cloud.work.dir',
                                    'ec2_cloud.template.config'])
            }
        }).done(_.bind(function (resp) {
            this.render();
            this.$('#g-ec2_cloud-provider-startcluster-work-dir').val(
                resp['ec2_cloud.work.dir']
            );
            this.$('#g-ec2_cloud-provider-starcluster-template-file').val(
                resp['ec2_cloud.template.config']
            );
        }, this));
    },

    render: function () {
        this.$el.html(jade.templates.ec2_cloud_config({}));

        if (!this.breadcrumb) {
            this.breadcrumb = new girder.views.PluginConfigBreadcrumbWidget({
                pluginName: 'EC2 Cloud Management',
                el: this.$('.g-config-breadcrumb-container')
            }).render();
        }

        return this;
    },

    _saveSettings: function (settings) {
        girder.restRequest({
            type: 'PUT',
            path: 'system/setting',
            data: {
                list: JSON.stringify(settings)
            },
            error: null
        }).done(_.bind(function (resp) {
            girder.events.trigger('g:alert', {
                icon: 'ok',
                text: 'Settings saved.',
                type: 'success',
                timeout: 4000
            });
        }, this)).error(_.bind(function (resp) {
            this.$('#g-ec2_cloud-provider-starcluster-error-message').text(
                resp.responseJSON.message);
        }, this));
    }
});

girder.router.route('plugins/ec2_cloud/config', 'ec2_cloudConfig', function () {
    girder.events.trigger('g:navigateTo', girder.views.ec2_cloud_ConfigView);
});
