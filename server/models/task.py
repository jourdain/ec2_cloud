#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright 2013 Kitware Inc.
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

import datetime

from girder.models.model_base import AccessControlledModel, ValidationException
from girder.constants import AccessType
from girder.plugins.ec2_cloud import constants

class Task(AccessControlledModel):
    """
    Tasks are used to define a task that should be run on a cluster.
    """

    def initialize(self):
        self.name = 'task_cloud'
        self.ensureIndices(['parentId', 'name', 'lowerName', 'status'])
        self.ensureTextIndex({
            'name': 10,
            'description': 1
        })

    def filter(self, task, user):
        """
        Filter a task document for display to the user.
        """
        keys = ['_id', 'name', 'description', 'created', 'updated', 'parentId', 'parentCollection', 'creatorId',
                'baseParentType', 'baseParentId', 'task', 'node', 'size', 'status', 'web', 'url']

        filtered = self.filterDocument(task, allow=keys)

        filtered['_accessLevel'] = self.getAccessLevel(task, user)

        return filtered

    def validate(self, doc):
        doc['name'] = doc['name'].strip()
        doc['lowerName'] = doc['name'].lower()
        doc['description'] = doc['description'].strip()

        if not doc['name']:
            raise ValidationException('Task name must not be empty.', 'name')

        if not doc['parentCollection'] in ('folder', 'user', 'collection'):
            # Internal error; this shouldn't happen
            raise Exception('Invalid task parent type: %s.' %
                            doc['parentCollection'])

        # Ensure unique name among sibling tasks
        q = {
            'parentId': doc['parentId'],
            'name': doc['name'],
            'parentCollection': doc['parentCollection']
        }
        if '_id' in doc:
            q['_id'] = {'$ne': doc['_id']}
        duplicates = self.find(q, limit=1, fields=['_id'])
        if duplicates.count() != 0:
            raise ValidationException('A task with that name already '
                                      'exists here.', 'name')

        # Ensure unique name among sibling items
        q = {
            'folderId': doc['parentId'],
            'name': doc['name']
        }
        duplicates = self.model('item').find(q, limit=1, fields=['_id'])
        if duplicates.count() != 0:
            raise ValidationException('An item with that name already '
                                      'exists here.', 'name')

        return doc

    def load(self, id, level=AccessType.ADMIN, user=None, objectId=True,
             force=False, fields=None, exc=False):
        """
        We override load in order to ensure the task has certain fields
        within it, and if not, we add them lazily at read time.

        :param id: The id of the resource.
        :type id: string or ObjectId
        :param user: The user to check access against.
        :type user: dict or None
        :param level: The required access type for the object.
        :type level: AccessType
        :param force: If you explicity want to circumvent access
                      checking on this resource, set this to True.
        :type force: bool
        """
        print "try to load ", id
        doc = AccessControlledModel.load(
            self, id=id, objectId=objectId, level=level, fields=fields,
            exc=exc, force=force, user=user)

        print 'got'
        print doc

        if doc is not None and 'baseParentType' not in doc:
            pathFromRoot = self.parentsToRoot(doc, user=user, force=force)
            baseParent = pathFromRoot[0]
            doc['baseParentId'] = baseParent['object']['_id']
            doc['baseParentType'] = baseParent['type']
            self.save(doc)
        if doc is not None and 'lowerName' not in doc:
            self.save(doc)

        return doc

    def move(self, task, parent, parentType):
        """
        Move the given task from its current parent to another parent object.

        :param task: The task to move.
        :type task: dict
        :param parent: The new parent object.
        :param parentType: The type of the new parent object (user, collection,
        or folder).
        :type parentType: str
        """
        task['parentId'] = parent['_id']
        task['parentCollection'] = parentType

        if parentType == 'folder':
            task['baseParentType'] = parent['baseParentType']
            task['baseParentId'] = parent['baseParentId']
        else:
            task['baseParentType'] = parentType
            task['baseParentId'] = parent['_id']

        return self.save(task)

    def remove(self, task):
        """
        Delete a task.

        :param task: The task document to delete.
        :type task: dict
        """
        # Delete this task
        AccessControlledModel.remove(self, task)

    def createTask(self, parent, name, description='', parentType='folder',
                    taskId=None, nodeId=None, clusterSize=1, creator=None, web=False):
        """
        Create a new task under the given parent.

        :param parent: The parent document. Should be a folder, user, or
                       collection.
        :type parent: dict
        :param name: The name of the task.
        :type name: str
        :param description: Description for the task.
        :type description: str
        :param parentType: What type the parent is:
                           ('folder' | 'user' | 'collection')
        :type parentType: str
        :param creator: User document representing the creator of this task.
        :type creator: dict
        :returns: The task document that was created.
        """
        assert '_id' in parent

        parentType = parentType.lower()
        if parentType not in ('folder', 'user', 'collection'):
            raise ValidationException('The parentType must be folder, '
                                      'collection, or user.')

        if parentType == 'folder':
            parentObject = {'parentId': parent['_id'],
                            'parentCollection': parentType}
            pathFromRoot = self.parentsToRoot(parentObject, user=creator)
            if 'baseParentId' not in parent:
                pathFromRoot = self.parentsToRoot(parent, user=creator)
                parent['baseParentId'] = pathFromRoot[0]['object']['_id']
                parent['baseParentType'] = pathFromRoot[0]['type']
        else:
            parent['baseParentId'] = parent['_id']
            parent['baseParentType'] = parentType

        now = datetime.datetime.now()

        if creator is None:
            creatorId = None
        else:
            creatorId = creator.get('_id', None)

        task = {
            'name': name,
            'description': description,
            'parentCollection': parentType,
            'baseParentId': parent['baseParentId'],
            'baseParentType': parent['baseParentType'],
            'parentId': parent['_id'],
            'creatorId': creatorId,
            'created': now,
            'updated': now,
            'status': constants.CloudTaskStatus.READY,
            'task': taskId,
            'node': nodeId,
            'size': clusterSize,
            'web': web,
            'url': ''
        }

        self.setUserAccess(task, user=creator, level=AccessType.ADMIN)

        # Now validate and save the task.
        return self.save(task)

    def updateTask(self, task):
        """
        Updates a task.

        :param task: The task document to update
        :type task: dict
        :returns: The task document that was edited.
        """
        task['updated'] = datetime.datetime.now()

        # Validate and save the task
        return self.save(task)

    def parentsToRoot(self, task_folder, curPath=[], user=None, force=False,
                      level=AccessType.READ):
        """
        Get the path to traverse to a root of the hierarchy.

        :param item: The item whose root to find
        :type item: dict
        :returns: an ordered list of dictionaries from root to the current item
        """
        curParentId = task_folder['parentId']
        curParentType = task_folder['parentCollection']
        curParentObject = self.model(curParentType).load(
            curParentId, user=user, level=level, force=force)
        parentFiltered = self.model(curParentType).filter(curParentObject,
                                                          user)
        return [{'type': curParentType,
                 'object': parentFiltered}] + curPath

    def childTasks(self, parent, parentType, user=None, limit=50, offset=0,
                     sort=None, filters={}):
        """
        This generator will yield child tasks of a user, collection, or
        folder, with access policy filtering.

        :param parent: The parent object.
        :type parentType: Type of the parent object.
        :param parentType: The parent type.
        :type parentType: 'user', 'folder', or 'collection'
        :param user: The user running the query. Only returns folders that this
                     user can see.
        :param limit: Result limit.
        :param offset: Result offset.
        :param sort: The sort structure to pass to pymongo.
        :param filters: Additional query operators.
        """
        parentType = parentType.lower()
        if parentType not in ('folder', 'user', 'collection'):
            raise ValidationException('The parentType must be folder, '
                                      'collection, or user.')

        q = {
            'parentId': parent['_id'],
            'parentCollection': parentType
        }
        q.update(filters)

        # Perform the find; we'll do access-based filtering of the result set
        # afterward.
        cursor = self.find(q, limit=0, sort=sort)

        for r in self.filterResultsByPermission(cursor=cursor, user=user,
                                                level=AccessType.READ,
                                                limit=limit, offset=offset):
            yield r

