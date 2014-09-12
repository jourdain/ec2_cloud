girder.App = Backbone.View.extend({
    el: 'body',

    events: {
        'click a.g-forgot-password': function () {
            girder.events.trigger('g:resetPasswordUi');
        },

        'click .g-register-link': function () {
            girder.events.trigger('g:registerUi');
        },

        'click .g-my-account-link': function () {
            girder.router.navigate('useraccount/' + girder.currentUser.get('_id') +
                                   '/info', {trigger: true});
        },

        'click .g-app-title' : function() {
            if(girder.currentUser) {
                girder.router.navigate('projects', {trigger: true});
            } else {
                girder.router.navigate('', {trigger: true});
            }
        },

        'submit #g-login-form': function (e) {
            e.preventDefault();

            var authStr = btoa(this.$('#g-login').val() + ':' +
                               this.$('#g-password').val());
            girder.restRequest({
                path: 'user/authentication',
                type: 'GET',
                headers: {
                    'Authorization': 'Basic ' + authStr
                },
                error: null // don't do default error behavior
            }).done(_.bind(function (resp) {
                // Save the token for later
                resp.user.token = resp.authToken.token;

                // Update user info
                girder.currentUser = new girder.models.UserModel(resp.user);

                // girder.events.trigger('g:login');
                this.render();
                girder.router.navigate('projects', {trigger: true});

            }, this)).error(_.bind(function (err) {
                this.$('.g-validation-failed-message').text(err.responseJSON.message);
                this.$('#g-login-button').removeClass('disabled');
            }, this));

            this.$('#g-login-button').addClass('disabled');
            this.$('.g-validation-failed-message').text('');
        }
    },

    initialize: function (settings) {
        girder.restRequest({ path: 'user/me' }).done(_.bind(function (user) {
            if (user) {
                girder.currentUser = new girder.models.UserModel(user);
            }
            this.render();

            // Once we've rendered the layout, we can start up the routing.
            Backbone.history.start({
                pushState: false
            });
        }, this));

        // Attach event listeners
        girder.events.on('g:navigateTo', this.navigateTo, this);
        girder.events.on('g:registerUi', this.registerDialog, this);
        girder.events.on('g:resetPasswordUi', this.resetPasswordDialog, this);
        girder.events.on('g:alert', this.alert, this);
        girder.events.on('g:login', this.login, this);
        girder.events.on('g:view', girder.vm.render, girder.vm);
        girder.events.on('g:data', girder.vm.update, girder.vm);
    },

    render: function () {
        this.$el.html(jade.templates.layout({
            currentUser: girder.currentUser
        }));

        if(girder.currentUser) {
            girder.events.trigger('g:data', { user: girder.currentUser });
            girder.vm.render('navigation');
        }

        return this;
    },

    /**
     * Changes the current body view to the view class specified by view.
     * @param view The view to display in the body.
     * @param [settings={}] Settings to pass to the view initialize() method.
     */
    navigateTo: function (view, settings) {
        var container = this.$('#g-app-body-container');
        settings = settings || {};

        if (view) {
            // Unbind all local events added by the previous body view.
            container.off();

            // Unbind all globally registered events from the previous view.
            if (this.bodyView) {
                girder.events.off(null, null, this.bodyView);
            }

            settings = _.extend(settings, {
                el: this.$('#g-app-body-container')
            });

            /* We let the view be created in this way even though it is
             * normally against convention.
             */
            /*jshint -W055 */
            this.bodyView = new view(settings);
        }
        else {
            console.error('Undefined page.');
        }
        return this;
    },

    registerDialog: function () {
        if (!this.userRegisterView) {
            this.userRegisterView = new girder.views.RegisterView({
                el: this.$('#g-dialog-container')
            });
        }
        this.userRegisterView.render();
    },

    resetPasswordDialog: function () {
        if (!this.resetPasswordView) {
            this.resetPasswordView = new girder.views.ResetPasswordView({
                el: this.$('#g-dialog-container')
            });
        }
        this.resetPasswordView.render();
    },

    /**
     * Display a brief alert on the screen with the following options:
     *   - text: The text to be displayed
     *   - [type]: The alert class ('info', 'warning', 'success', 'danger').
     *             Default is 'info'.
     *   - [icon]: An optional icon to display in the alert.
     *   - [timeout]: How long before the alert should automatically disappear.
     *                Default is 6000ms. Set to <= 0 to have no timeout.
     */
    alert: function (options) {
        var el = $(jade.templates.alert({
            text: options.text,
            type: options.type || 'info',
            icon: options.icon
        }));
        $('#g-alerts-container').append(el);
        el.fadeIn(500);

        if (options.timeout === undefined) {
            options.timeout = 6000;
        }
        if (options.timeout > 0) {
            window.setTimeout(function () {
                el.fadeOut(750, function () {
                    $(this).remove();
                });
            }, options.timeout);
        }
    },

    /**
     * On login or logout, we re-render the current body view.
     */
    login: function () {
        girder.router.navigate('', {trigger: true});
        this.render();
    }
});
