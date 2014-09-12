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

import sys, os, errno, json, logging
import starcluster.config

from starcluster import exception

# Enable starcluster debug output
_configuration = None
startcluster_debug = True

if startcluster_debug:
    log = logging.getLogger('starcluster')
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)

def _exists(path):
    return os.path.isfile(path)

def _load_configuration(path):
    data = None
    with open(path, 'r') as json_file:
        data = json.load(json_file)

    return data

def _mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def create_configuration(configurationFilePath, tasks, template_file):
    global _configuration
    if not _configuration:
        _configuration = _load_configuration('/Volumes/KSSD/code/Girder/src/plugins/ec2_cloud/sc_plugins/cloud_config.json')

    _mkdir(os.path.dirname(configurationFilePath))
    clusterNames = []
    with open(template_file, 'r') as header:
        with open(configurationFilePath, 'w') as config:
            config.write(header.read())
            config.write("\n### Custom configuration ###\n")

            for task in tasks:
                uid = "%s_%s" % (task['task'], task['_id'].__str__())

                # Handle initialization
                pluginList = []
                pluginList.extend(_configuration['nodes'][task['node']]['plugins'])
                pluginList.append("mpi_" + uid)
                pluginList.append(uid)

                clusterNames.append(uid)

                config.write("\n[cluster %s]\n" % uid)
                config.write("EXTENDS = default_cluster\n")
                config.write("CLUSTER_SIZE = %d\n" % task['size'])
                config.write("PLUGINS = %s\n" % ", ".join(pluginList))
                config.write("NODE_INSTANCE_TYPE = %s\n" % task['node'])
                config.write("MASTER_INSTANCE_TYPE = %s\n" % task['node'])
                config.write("USERDATA_SCRIPTS = %s\n" % _configuration['nodes'][task['node']]['scripts'])

                # Define task plugin
                config.write("\n[plugin %s]\n" % uid)
                config.write("setup_class = common_tasks.GenericTaskRunner\n")
                config.write("script_path = %s\n" % _configuration['tasks'][task['task']])
                config.write("args = \n")

                # Define MPI config plugin
                config.write("\n[plugin mpi_%s]\n" % uid)
                config.write("setup_class = common_tasks.CreateMPIHostFile\n")
                config.write("number_of_nodes = %s\n" % task['size'])
                config.write("number_of_cpu = %s\n" % _configuration['nodes'][task['node']]['cpu'])

    # Try to load and validate configuration
    cfg = starcluster.config.StarClusterConfig(configurationFilePath);
    cfg.load()
    result = True
    for clusterName in clusterNames:
        sc = cfg.get_cluster_template(clusterName, clusterName)
        result = sc.is_valid() and result

    # Make sure it is valid
    return result

def start_cluster(configurationFilePath, clusterName, newCluster):
    if not _exists(configurationFilePath):
        return False

    # Configure starcluster with cluster definition
    cfg = starcluster.config.StarClusterConfig(configurationFilePath);
    cfg.load()
    sc = cfg.get_cluster_template(clusterName, clusterName)
    if sc.is_valid():
        sc.start(create=newCluster)
        return True

    return False

def list_clusters(configurationFilePath):
    if not _exists(configurationFilePath):
        return []

    cfg = starcluster.config.StarClusterConfig(configurationFilePath);
    cfg.load()
    sc = cfg.get_cluster_manager()
    clusterList = []

    cluster_groups = sc.get_cluster_security_groups()

    for scg in cluster_groups:
        tag = sc.get_tag_from_sg(scg.name)
        try:
            cl = sc.get_cluster(tag, group=scg, load_plugins=False,
                                  load_volumes=False, require_keys=False)
        except exception.IncompatibleCluster as e:
            continue

        nodes = cl.nodes
        size = 0
        try:
            n = nodes[0]
            size = len(nodes)
        except IndexError:
            n = None

        clusterList.append({
            "name" : tag,
            "zone": getattr(n, 'placement', 'N/A'),
            "size": size,
            "uptime": getattr(n, 'uptime', 'N/A'),
            "state": getattr(n, 'state', 'N/A'),
            "type": getattr(n, 'instance_type', 'N/A'),
            "subnet": getattr(n, 'subnet_id', 'N/A'),
            "group": getattr(n, 'groups', 'N/A'),
            "ip": getattr(n, 'ip_address', ''),
            "dns": getattr(n, 'addr', ''),
            "task": tag[-24:]
        });

    return clusterList

def stop_cluster(configurationFilePath, clusterName):
    if not _exists(configurationFilePath):
        return False

    # Configure starcluster with cluster definition
    cfg = starcluster.config.StarClusterConfig(configurationFilePath);
    cfg.load()
    sc = cfg.get_cluster_manager()
    sc.terminate_cluster(clusterName, force=True)
    return True
