var girder = _.extend(girder, {
    mixins : {},
    vm : (function() {
            var viewMap = {},
                activeViewMap = {},
                activeData = {};

            function _methodName(str) {
                return 'set' + str.charAt(0).toUpperCase() + str.slice(1);
            }

            function update(map) {
                _.each(map, function(value, key) {
                    // console.log('GIRDER: update data: ' + key);
                    if(activeData.hasOwnProperty(key)) {
                        activeData[key].data = value;
                    } else {
                        activeData[key] = {
                            data: value,
                            dependency: []
                        };
                    }

                    // Update dependent views
                    // console.log(_methodName(key) + ' on ' + activeData[key].dependency.join(', '));
                    _.each(activeData[key].dependency, function(viewName) {
                        view(viewName)[_methodName(key)](value);
                        invalidate(viewName);
                    });
                });
            }

            function register(instance, selector) {
                var name = instance.getName(),
                    dependency = instance.getSubViews(),
                    mixins = instance.getDataDependency();

                viewMap[name] = { view: instance, selector: selector, dependency: dependency || []};
                _.each(mixins || [], function(dataDependency) {
                    if(!activeData.hasOwnProperty(dataDependency)) {
                        activeData[dataDependency] = {
                            data: null,
                            dependency: [ name ]
                        };
                    } else {
                         activeData[dataDependency].dependency.push(name);
                    }
                });
            }

            function render(name) {
                // console.log('GIRDER: activate view ' + name);
                viewMap[name].view.setElement($(viewMap[name].selector)).render();
                activeViewMap[viewMap[name].selector] = name;
                _.each(viewMap[name].dependency, function(viewName) {
                    render(viewName);
                });
            }

            function invalidate(name) {
                if(activeViewMap[viewMap[name].selector] === name) {
                    render(name);
                }
            }

            function view(name) {
                return viewMap[name].view;
            }

            return {
                view : view,
                invalidate : invalidate,
                render : render,
                register : register,
                update : update
            };
        })()
});