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

from girder import events
from girder.models.model_base import ValidationException
from . import rest, constants

def validateSettings(event):
    key, val = event.info['key'], event.info['value']

    if key == constants.PluginSettings.STARCLUSTER_WORK_DIRECTORY:
        if not val:
            raise ValidationException(
                'The path for the plugin working directory.', 'value')
        event.preventDefault().stopPropagation()
    elif key == constants.PluginSettings.STARCLUSTER_TEMPLATE_CONFIGURATION_PATH:
        if not val:
            raise ValidationException(
                'Path to an initial Starcluster configuration file.', 'value')
        event.preventDefault().stopPropagation()


def load(info):
    # Attach plugin configuration
    events.bind('model.setting.validate', 'ec2_cloud', validateSettings)

    # Serve custom client
    info['config']['/cloud'] = {
        'tools.staticdir.on': 'True',
        'tools.staticdir.index': 'index.html',
        'tools.staticdir.dir': 'plugins/ec2_cloud/www'
    }

    # Add Restful api
    info['apiRoot'].task = rest.Task()

    # Copy Girder API over
    # serverRoot.cloud.api = serverRoot.api.v1
