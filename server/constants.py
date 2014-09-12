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

"""
Constants should be defined here.
"""
import os

# Constants representing the setting keys for this plugin
class PluginSettings:
    STARCLUSTER_WORK_DIRECTORY = 'ec2_cloud.work.dir'
    STARCLUSTER_TEMPLATE_CONFIGURATION_PATH = 'ec2_cloud.template.config'

class CloudTaskStatus(object):
    """
    Provides a set of values for Cloud Task Status.
    """
    ERROR   = 0
    READY   = 1
    PENDING = 2
    RUNNING = 3
    DONE = 4

    @staticmethod
    def toString(value):
        if value == 0:
            return 'Error'
        elif value == 1:
            return 'Ready'
        elif value == 2:
            return 'Pending'
        elif value == 3:
            return 'Running'
        elif value == 4:
            return 'Completed'
        else:
            return 'Undefined'

