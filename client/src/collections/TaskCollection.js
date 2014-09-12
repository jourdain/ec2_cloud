girder.collections.TaskCollection = girder.Collection.extend({
    resourceName: 'task',
    sortField: 'lowerName',
    model: girder.models.TaskModel,

    pageLimit: 100,

    comparator: null
});
