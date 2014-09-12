#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################

from types import *
import sys, traceback, os, json

from girder import events
from girder.constants import AccessType
from girder.utility.model_importer import ModelImporter
from girder.api.describe import Description
from girder.api.rest import Resource, RestException, loadmodel

from girder.plugins.ec2_cloud import constants
from girder.plugins.ec2_cloud import ec2_controller

class __old_task_stuff__(Resource):
    """API Endpoint for Ec2 Cloud tasks."""

    def __init__(self):
        self.resourceName = 'ec2_cloud'

        self.route('POST', ('createTask', ':name', ':task', ':cluster',), self.createTask)
        self.route('DELETE', ('deleteTask', ':id',), self.deleteTask)
        self.route('POST', ('start', ':name',), self.start)
        self.route('POST', ('stop', ':name',), self.stop)
        self.route('GET', ('status', ':name',), self.status)

    @loadmodel(map={'id': 'task'}, model='task', plugin='ec2_cloud', level=AccessType.ADMIN)
    def deleteTask(self, task, params):
        """
        Delete a task
        """
        self.model('task', 'ec2_cloud').remove(task)
        return {'message': 'Deleted task {}.'.format(task['name'])}
    deleteTask.description = (
        Description('Delete a task by its ID.')
        .param('id', 'The ID of the task.', paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('Admin access was denied for the item.', 403))

    def createTask(self, name, task, cluster, params):
        """
        Create a new task for the given user
        using metadata for /templates/tasks/item and /templates/clusters/item
        """
        description = params.get('description', '')
        print "Web value ", params.get('web', '0')
        webEndpoint = False if str(params.get('web', '0')) == '0' else True
        me = self.getCurrentUser()

        # Make sure we have a folder for our tasks
        userTasksFolderCursor = self.model('folder').find({'lowerName': 'tasks', 'parentId': me['_id']})
        if userTasksFolderCursor.count() == 0:
            # Need to create a folder "Tasks" for current user
            userTasksFolder = self.model('folder').createFolder(me, 'Tasks', 'User tasks for Cloud execution', 'user', False, me)
        else:
            userTasksFolder = userTasksFolderCursor.next();

        # Lookup templates
        templates = self.model('collection').find({'name': 'templates'}).next()['_id']
        cluster_template_dir = self.model('folder').find({'lowerName': 'clusters', 'parentId': templates}).next()['_id']
        task_template_dir = self.model('folder').find({'lowerName': 'tasks', 'parentId': templates}).next()['_id']
        cluster_template = self.model('item').find({'folderId': cluster_template_dir, 'name': cluster})
        task_template = self.model('item').find({'folderId': task_template_dir, 'name': task})

        if task_template.count() == 0:
            raise RestException('Invalid template name for task.', code=401)
        taskTemplateMetaObj = task_template.next()
        taskTemplateMeta = {}
        if 'meta' in taskTemplateMetaObj:
            taskTemplateMeta = taskTemplateMetaObj['meta']

        if cluster_template.count() == 0:
            raise RestException('Invalid template name for cluster.', code=402)
        clusterTemplateMetaObj = cluster_template.next()
        clusterTemplateMeta = {}
        if 'meta' in clusterTemplateMetaObj:
            clusterTemplateMeta = clusterTemplateMetaObj['meta']

        return self.model('task', 'ec2_cloud').createTask(userTasksFolder, name, description,
                          parentType = 'folder',
                          taskTemplate = taskTemplateMeta,
                          clusterTemplate = clusterTemplateMeta,
                          creator = me,
                          web = webEndpoint)

    createTask.description = (
        Description(
            'Create a task in the cloud for a given user'
        )
        .param(
            'name',
            'Name for the new task.',
            required=True, paramType='path')
        .param(
            'description',
            'Description for the new task.'+
            '(default="(empty)")',
            required=False)
        .param(
            'web',
            'Does that task has a Web endpoint when running.'+
            '(default=False)',
            required=False)
        .param(
            'task',
            'Name of a template task.',
            required=True, paramType='path')
        .param(
            'cluster',
            'Name of a template cluster.',
            required=True, paramType='path')
        .errorResponse()
        .errorResponse('No task found with given name.', 401)
        .errorResponse('No cluster found with given name.', 402)
        .errorResponse('Error while creating task.', 403)
    )

    def start(self, name, params):
        taskToStartCursor = self.model('task', 'ec2_cloud').find({'name': name})

        if taskToStartCursor.count() == 0:
            raise RestException('No task found.', code=401)

        taskToStart = taskToStartCursor.next()
        if taskToStart['status'] != 1:
            raise RestException('Invalid task status {}.'.format(constants.CloudTaskStatus.toString(taskToStart['status'])), code=402)



        # create cluster config
        login = self.getCurrentUser()['login']
        taskId = taskToStart['_id'].__str__()
        clusterId = "%s_%s" % (login, taskId)
        template_file_path = self.model('setting').get(constants.PluginSettings.STARCLUSTER_TEMPLATE_CONFIGURATION_PATH)
        working_dir = self.model('setting').get(constants.PluginSettings.STARCLUSTER_WORK_DIRECTORY)
        configurationFilePath = os.path.join(working_dir, login, taskId)

        # configurationFilePath, task, template_file, clusterName
        if not ec2_controller.create_configuration(configurationFilePath, taskToStart, template_file_path, clusterId):
            raise RestException('Invalid configuration {}.'.format(working_dir), code=403)

        # start cluster
        if not ec2_controller.start_cluster(configurationFilePath, clusterId):
            raise RestException('Error while starting cluster. {}'.format(working_dir), code=404)

        # FIXME queue the task
        # FIXME backup the data
        # FIXME stop cluster once task is done

        taskToStart['status'] = constants.CloudTaskStatus.RUNNING
        self.model('task', 'ec2_cloud').updateTask(taskToStart)

        return taskToStart

    start.description = (
        Description(
            'Start the task and return it.'
        )
        .param(
            'name',
            'The task name.',
            required=True, paramType='path')
        .errorResponse()
        .errorResponse('No task found with given name.', 401)
        .errorResponse('Task not in ready state.', 402)
        .errorResponse('Invalid generated configuration for task.', 403)
        .errorResponse('Error while starting cluster.', 404)
    )

    def stop(self, name, params):
        taskToStopCursor = self.model('task', 'ec2_cloud').find({'name': name})

        if taskToStopCursor.count() == 0:
            raise RestException('No task found.', code=401)

        taskToStop = taskToStopCursor.next()
        if taskToStop['status'] != constants.CloudTaskStatus.RUNNING:
            raise RestException('Invalid task status {}.'.format(constants.CloudTaskStatus.toString(taskToStop['status'])), code=402)

        # terminate cluster
        login = self.getCurrentUser()['login']
        taskId = taskToStop['_id'].__str__()
        clusterId = "%s_%s" % (login, taskId)
        template_file_path = self.model('setting').get(constants.PluginSettings.STARCLUSTER_TEMPLATE_CONFIGURATION_PATH)
        working_dir = self.model('setting').get(constants.PluginSettings.STARCLUSTER_WORK_DIRECTORY)
        configurationFilePath = os.path.join(working_dir, login, taskId)
        if not ec2_controller.stop_cluster(configurationFilePath, clusterId):
            raise RestException('Error while terminate cluster. {}'.format(working_dir), code=403)

        taskToStop['status'] = constants.CloudTaskStatus.READY
        self.model('task', 'ec2_cloud').updateTask(taskToStop)

        # FIXME kill task
        # FIXME backup the data
        # FIXME stop cluster once task

        return taskToStop

    stop.description = (
        Description(
            'Stop the cluster and returns its specifications.'
        )
        .param(
            'name',
            'The task name.',
            required=True, paramType='path')
        .errorResponse()
        .errorResponse('No task found with given name.', 401)
        .errorResponse('Task not in RUNNING state.', 402)
        .errorResponse('No task found with given name.', 403)
    )

    def status(self, name, params):
        """
        Return task status
            {
                task: 'RUNNING',
                cluster: { name: 'wefg1324tsdg', running: True, load: [0.23, 0.1, 0.3] }
            }
        """
        taskCursor = self.model('task', 'ec2_cloud').find({'name': name})
        if taskCursor.count() == 0:
            raise RestException('No task found.', code=401)

        # FIXME probe cluster
        # FIXME generate result object

        return taskCursor.next()

    status.description = (
        Description(
            'Returns the cluster description.'
        )
        .param(
            'id',
            'The cluster ID.',
            required=False)
        .errorResponse()
        .errorResponse('No task found with given name.', 401)
    )

# =============================================================================

class Task(Resource):

    def __init__(self):
        self.resourceName = 'task'
        self.route('POST', (), self.createTask)
        self.route('DELETE', (':id',), self.deleteTask)
        self.route('DELETE', ('cluster', ':id',), self.stopCluster)
        self.route('GET', (), self.find)
        self.route('GET', (':id',), self.getTask)
        self.route('GET', ('clusters',':id',), self.listClusters)
        self.route('GET', ('tasks',':id',), self.updateTasks)
        self.route('PUT', (':id',), self.updateTask)
        self.route('PUT', ('start', ':id',), self.startTask)

    def find(self, params):
        """
        Get a list of tasks with given search parameters. Currently accepted
        search modes are:

        1. Searching by parentId and parentType.
        2. Searching with full text search.

        To search with full text search, pass the "text" parameter. To search
        by parent, (i.e. list child folders) pass parentId and parentType,
        which must be one of ('folder' | 'collection' | 'user'). You can also
        pass limit, offset, sort, and sortdir paramters.

        :param limit: The result set size limit, default=50.
        :param offset: Offset into the results, default=0.
        :param sort: The field to sort by, default=lowerName.
        :param sortdir: 1 for ascending, -1 for descending, default=1.
        """
        limit, offset, sort = self.getPagingParameters(params, 'lowerName')
        user = self.getCurrentUser()

        if 'parentId' in params and 'parentType' in params:
            parentType = params['parentType'].lower()
            if parentType not in ('collection', 'folder', 'user'):
                raise RestException('The parentType must be user, collection,'
                                    ' or folder.')

            parent = self.model(parentType).load(
                id=params['parentId'], user=user, level=AccessType.READ,
                exc=True)

            filters = {}
            if 'text' in params:
                filters['$text'] = {
                    '$search': params['text']
                }

            return [self.model('task', 'ec2_cloud').filter(folder, user) for folder in
                    self.model('task', 'ec2_cloud').childTasks(
                        parentType=parentType, parent=parent, user=user,
                        offset=offset, limit=limit, sort=sort, filters=filters)]
        elif 'text' in params:
            return [self.model('task', 'ec2_cloud').filter(task, user) for task in
                    self.model('task', 'ec2_cloud').textSearch(
                        params['text'], user=user, limit=limit, offset=offset,
                        sort=sort)]
        else:
            raise RestException('Invalid search mode.')
    find.description = (
        Description('Search for tasks by certain properties.')
        .responseClass('Task')
        .param('parentType', """Type of the folder's parent: either user,
               folder, or collection (default='folder').""", required=False)
        .param('parentId', "The ID of the folder's parent.", required=False)
        .param('text', 'Pass to perform a text search.', required=False)
        .param('limit', "Result set size limit (default=50).", required=False,
               dataType='int')
        .param('offset', "Offset into result set (default=0).", required=False,
               dataType='int')
        .param('sort', "Field to sort the folder list by (default=name)",
               required=False)
        .param('sortdir', "1 for ascending, -1 for descending (default=1)",
               required=False, dataType='int')
        .errorResponse()
        .errorResponse('Read access was denied on the parent resource.', 403))

    @loadmodel(map={'id': 'task'}, model='task', plugin='ec2_cloud', level=AccessType.ADMIN)
    def updateTask(self, task, params):
        user = self.getCurrentUser()
        task['name'] = params.get('name', task['name']).strip()
        task['description'] = params.get('description', task['description']).strip()
        task['task'] = params.get('task', task['task']).strip()
        task['node'] = params.get('node', task['node']).strip()
        task['size'] = int(params.get('size', task['size']))
        task['web'] = not not int(params.get('web', '1' if 'web' in task else '0'))

        # DEBUG
        task['status'] = constants.CloudTaskStatus.READY

        task = self.model('task', 'ec2_cloud').updateTask(task)

        if 'parentType' in params and 'parentId' in params:
            parentType = params['parentType'].lower()
            if parentType not in ('user', 'collection', 'folder'):
                raise RestException('Invalid parentType.')

            parent = self.model(parentType).load(
                params['parentId'], level=AccessType.WRITE, user=user, exc=True)

            task = self.model('task', 'ec2_cloud').move(task, parent, parentType)

        # Update configuration
        self._updateConfiguration(task["parentId"].__str__())

        return self.model('task', 'ec2_cloud').filter(task, user)
    updateTask.description = (
        Description('Update a task or move it into a new parent.')
        .responseClass('Task')
        .param('id', 'The ID of the task.', paramType='path')
        .param('name', 'Name of the task.', required=False)
        .param('description', 'Description for the task.', required=False)
        .param('taskId', 'Identifier for cluster available task.', required=False)
        .param('nodeId', 'Identifier for cluster node type.', required=False)
        .param('clusterSize', 'Number of computer that will compose the cluster', required=False)
        .param('parentType', 'Parent type for the new parent of this task.',
               required=False)
        .param('parentId', 'Parent ID for the new parent of this task.',
               required=False)
        .param('web', 'This task has a web end point or not.',
               required=False)
        .errorResponse('ID was invalid.')
        .errorResponse('Write access was denied for the task or its new '
                       'parent object.', 403))

    def createTask(self, params):
        """
        Create a new task.

        :param parentId: The _id of the parent folder.
        :type parentId: str
        :param parentType: The type of the parent of this folder.
        :type parentType: str - 'user', 'collection', or 'folder'
        :param name: The name of the task to create.
        :param description: Task description.
        :param public: Public read access flag.
        :type public: bool
        """
        self.requireParams(('name', 'parentId'), params)

        user = self.getCurrentUser()
        parentType = params.get('parentType', 'folder').lower()
        name = params['name'].strip()
        description = params.get('description', '').strip()
        taskId = params.get('task','').strip()
        nodeId = params.get('node','').strip()
        clusterSize = int(params.get('size', 1))
        public = self.boolParam('public', params, default=None)
        has_endpoint = False if params.get('web','0') == '0' else True

        if parentType not in ('folder', 'user', 'collection'):
            raise RestException('Set parentType to collection, folder, '
                                'or user.')

        model = self.model(parentType)

        parent = model.load(id=params['parentId'], user=user,
                            level=AccessType.WRITE, exc=True)

        task = self.model('task', 'ec2_cloud').createTask(
            parent=parent, name=name, parentType=parentType, creator=user,
            description=description,
            clusterSize=clusterSize, taskId=taskId, nodeId=nodeId, web=has_endpoint)

        if parentType in ('user', 'collection'):
            task = self.model('task', 'ec2_cloud').setUserAccess(
                task, user=user, level=AccessType.ADMIN, save=True)

        # Update configuration
        self._updateConfiguration(task["parentId"].__str__())

        return self.model('task', 'ec2_cloud').filter(task, user)
    createTask.description = (
        Description('Create a new task.')
        .responseClass('Task')
        .param('name', "Name of the task.")
        .param('task', 'Identifier for cluster available task.', required=True)
        .param('node', 'Identifier for cluster node type.', required=True)
        .param('size', 'Number of computer that will compose the cluster', required=True)
        .param('parentType', """Type of the folder's parent: either user,
               folder', or collection (default='folder').""", required=False)
        .param('parentId', "The ID of the task's parent.")
        .param('description', "Description for the task.", required=False)
        .param('web', 'This task has a web end point or not. (0 or 1)',
               required=False)
        .errorResponse()
        .errorResponse('Write access was denied on the parent', 403))

    @loadmodel(map={'id': 'task'}, model='task', plugin='ec2_cloud', level=AccessType.READ)
    def getTask(self, task, params):
        """Get a task by ID."""
        return self.model('task','ec2_cloud').filter(task, self.getCurrentUser())
    getTask.description = (
        Description('Get a task by ID.')
        .responseClass('Task')
        .param('id', 'The ID of the task.', paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('Read access was denied for the task.', 403))

    @loadmodel(map={'id': 'task'}, model='task', plugin='ec2_cloud', level=AccessType.ADMIN)
    def deleteTask(self, task, params):
        """
        Delete a folder recursively.
        """
        self.model('task', 'ec2_cloud').remove(task)
        return {'message': 'Deleted task %s.' % task['name']}
    deleteTask.description = (
        Description('Delete a task by ID.')
        .param('id', 'The ID of the task.', paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('Admin access was denied for the task.', 403))

    @loadmodel(map={'id': 'task'}, model='task', plugin='ec2_cloud', level=AccessType.ADMIN)
    def startTask(self, task, params):
        # create cluster config
        if not self._updateConfiguration(task["parentId"].__str__()):
            raise RestException('Invalid configuration.', code=403)

        # start cluster
        # FIXME not yet | if not ec2_controller.start_cluster(configurationFilePath, clusterId):
        # FIXME not yet |     raise RestException('Error while starting cluster. {}'.format(working_dir), code=404)

        # FIXME queue the task
        # FIXME backup the data
        # FIXME stop cluster once task is done

        # create cluster config
        clusterId = "%s_%s" % (task['task'], task['_id'].__str__())
        working_dir = self.model('setting').get(constants.PluginSettings.STARCLUSTER_WORK_DIRECTORY)
        configurationFilePath = os.path.join(working_dir, task["parentId"].__str__())

        # Start task on cluster
        ec2_controller.start_cluster(configurationFilePath, clusterId, True)

        # Update task status
        task['status'] = constants.CloudTaskStatus.RUNNING
        self.model('task', 'ec2_cloud').updateTask(task)

    startTask.description = (
        Description('Start a cluster for the task with ID.')
        .param('id', 'The ID of the task.', paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('Admin access was denied for the task.', 403))

    def updateTasks(self, id, params):
        working_dir = self.model('setting').get(constants.PluginSettings.STARCLUSTER_WORK_DIRECTORY)
        configurationFilePath = os.path.join(working_dir, id.__str__())

        # build cluster status indexed by task
        clusterMap = {}
        for cluster in ec2_controller.list_clusters(configurationFilePath):
            clusterMap[cluster['name']] = {
                "status": cluster['state'],
                "url" : "http://" + cluster['dns']
            }

        # Build task map
        taskMap = {}
        for task in self.find({ "parentType": "folder", "parentId": id }):
            taskMap["%s_%s" % (task['task'], task['_id'])] = task

        # Update tasks status and URL if need be
        for id in taskMap:
            task = self.model('task', 'ec2_cloud').load(taskMap[id]['_id'], user=self.getCurrentUser())
            if id in clusterMap:
                task['status'] = constants.CloudTaskStatus.RUNNING if clusterMap[id]["status"] == 'running' else constants.CloudTaskStatus.PENDING
                task['url'] = clusterMap[id]["url"]
            else:
                task['status'] = constants.CloudTaskStatus.READY

            print "Update task", id
            self.model('task', 'ec2_cloud').updateTask(task)

    updateTasks.description = (
        Description('Update tasks status.')
        .param('id', 'The ID of the project.', paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('Admin access was denied for the project.', 403))

    def listClusters(self, id, params):
        working_dir = self.model('setting').get(constants.PluginSettings.STARCLUSTER_WORK_DIRECTORY)
        configurationFilePath = os.path.join(working_dir, id)

        # Make sure user as access to project
        # FIXME

        return ec2_controller.list_clusters(configurationFilePath)

    listClusters.description = (
        Description('List clusters defined for the given project.')
        .param('id', 'The ID of the project.', paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('Admin access was denied for the project.', 403))

    @loadmodel(map={'id': 'task'}, model='task', plugin='ec2_cloud', level=AccessType.ADMIN)
    def stopCluster(self, task, params):
        clusterId = "%s_%s" % (task['task'], task['_id'].__str__())
        working_dir = self.model('setting').get(constants.PluginSettings.STARCLUSTER_WORK_DIRECTORY)
        configurationFilePath = os.path.join(working_dir, task["parentId"].__str__())

        # Stop cluster
        ec2_controller.stop_cluster(configurationFilePath, clusterId)

        # Update task status
        task['status'] = constants.CloudTaskStatus.READY
        self.model('task', 'ec2_cloud').updateTask(task)
    stopCluster.description = (
        Description('Stop a running cluster.')
        .param('id', 'The ID of the task.', paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('Admin access was denied for the project.', 403))

    def _updateConfiguration(self, projectId):
        # create cluster config
        template_file_path = self.model('setting').get(constants.PluginSettings.STARCLUSTER_TEMPLATE_CONFIGURATION_PATH)
        working_dir = self.model('setting').get(constants.PluginSettings.STARCLUSTER_WORK_DIRECTORY)
        configurationFilePath = os.path.join(working_dir, projectId)

        # configurationFilePath, tasks, template_file
        tasks = self.find({ "parentType": "folder", "parentId": projectId })

        return ec2_controller.create_configuration(configurationFilePath, tasks, template_file_path)

# =============================================================================

class Cluster(Resource):
    def __init__(self):
        self.resourceName = 'cluster'



