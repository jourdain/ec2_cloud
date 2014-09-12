module.exports = function (grunt) {

    grunt.config.merge({
        jade: {
            ec2_cloud_www: {
                files: {
                    'plugins/ec2_cloud/client/built/templates.js': [
                        'clients/web/src/templates/**/*.jade',
                        '!clients/web/src/templates/body/frontPage.jade',
                        '!clients/web/src/templates/layout/layout.jade',
                        '!clients/web/src/templates/layout/layoutHeader.jade',
                        '!clients/web/src/templates/layout/layoutHeaderUser.jade',
                        '!clients/web/src/templates/widgets/editFolderWidget.jade',
                        'plugins/ec2_cloud/client/src/templates/**/*.jade'
                    ]
                }
            }
        },

        stylus: {
            ec2_cloud_www: {
                files: {
                    'plugins/ec2_cloud/www/app.min.css': [
                        'clients/web/src/stylesheets/**/*.styl',
                        '!clients/web/src/stylesheets/apidocs/*.styl',
                        '!clients/web/src/stylesheets/layout/layout.styl',
                        'plugins/ec2_cloud/client/src/stylesheets/**/*.styl'
                    ]
                }
            }
        },

        uglify: {
            ec2_cloud_www_app: {
                files: {
                    'plugins/ec2_cloud/www/app.min.js': [
                        'plugins/ec2_cloud/client/built/templates.js',
                        'clients/web/src/init.js',
                        'plugins/ec2_cloud/client/src/init.js',
                        'plugins/ec2_cloud/client/src/app.js',
                        'plugins/ec2_cloud/client/src/mixins/*.js',
                        'clients/web/src/router.js',
                        'clients/web/src/utilities/**/*.js',
                        'clients/web/src/plugin_utils.js',
                        'clients/web/src/collection.js',
                        'clients/web/src/model.js',
                        'plugins/ec2_cloud/client/src/view.js',
                        'clients/web/src/models/**/*.js',
                        'clients/web/src/collections/**/*.js',
                        'clients/web/src/views/**/*.js',
                        '!clients/web/src/views/body/FrontPageView.js',
                        'plugins/ec2_cloud/client/src/models/**/*.js',
                        'plugins/ec2_cloud/client/src/collections/**/*.js',
                        'plugins/ec2_cloud/client/src/views/**/*.js',
                        'plugins/ec2_cloud/client/src/config.js'
                    ],
                    'plugins/ec2_cloud/www/main.min.js': [
                        'clients/web/src/main.js'
                    ]
                }
            },
            ec2_cloud_www_libs: {
                files: {
                    'plugins/ec2_cloud/www/libs.min.js': [
                        'node_modules/jquery-browser/lib/jquery.js',
                        'node_modules/jade/runtime.js',
                        'node_modules/underscore/underscore.js',
                        'node_modules/backbone/backbone.js',
                        'clients/web/lib/js/bootstrap.js',
                        'clients/web/lib/js/bootstrap-switch.js'
                    ],
                    'plugins/ec2_cloud/www/testing.min.js': [
                        'clients/web/test/lib/jasmine-1.3.1/jasmine.js',
                        'node_modules/blanket/dist/jasmine/blanket_jasmine.js',
                        'clients/web/test/lib/jasmine-1.3.1/ConsoleReporter.js'
                    ]
                }
            }
        },

        copy: {
            ec2_cloud_www: {
                files: [{
                    expand: true,
                    cwd: 'plugins/ec2_cloud/client/static',
                    src: ['**'],
                    dest: 'plugins/ec2_cloud/www'
                }]
            },
            ec2_cloud_lib: {
                files: [{
                    expand: true,
                    cwd: 'clients/web/static/lib',
                    src: ['bootstrap/**','fontello/**'],
                    dest: 'plugins/ec2_cloud/www/lib'
                }]
            },
        },

         watch: {
            ec2_cloud_stylus: {
                files: ['plugins/ec2_cloud/client/src/stylesheets/**/*.styl'],
                tasks: ['stylus:ec2_cloud_www', 'uglify:ec2_cloud_www_app']
            },
            ec2_cloud_jade: {
                files: ['plugins/ec2_cloud/client/src/templates/**/*.jade'],
                tasks: ['jade:ec2_cloud_www', 'uglify:ec2_cloud_www_app']
            },
            ec2_cloud_app: {
                files: ['plugins/ec2_cloud/client/src/**/*.js'],
                tasks: ['uglify:ec2_cloud_www_app']
            },
            ec2_cloud_static: {
                files: ['plugins/ec2_cloud/client/static/**'],
                tasks: ['copy:ec2_cloud_www']
            }
        }
    });

    // Register plugin name as task
    grunt.registerTask('ec2_cloud', ['uglify:ec2_cloud_www_app', 'uglify:ec2_cloud_www_libs', 'copy:ec2_cloud_www', 'copy:ec2_cloud_lib']);
};