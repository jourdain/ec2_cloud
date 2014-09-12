from starcluster.clustersetup import ClusterSetup
from starcluster.logger import log

class GenericTaskRunner(ClusterSetup):
    def __init__(self, script_path, args = [], all_nodes = False):
        self.script_path = script_path
        self.args = args
        self.all_nodes = all_nodes
        log.debug('script_path = %s' % script_path)
        log.debug('args = [%s]' % ', '.join(args))

    def run(self, nodes, master, user, user_shell, volumes):
        cmd = self.script_path + " " + " ".join(self.args)
        if self.all_nodes:
            log.info("running cmd as %s on all nodes: %s"  % (user,cmd) )
            for node in nodes:
                node.ssh.execute(cmd)
        else:
            log.info("running cmd as %s on master: %s"  % (user,cmd) )
            master.ssh.execute(cmd)

class CreateMPIHostFile(ClusterSetup):
    def __init__(self, number_of_nodes, number_of_cpu=1, hostfile_path='/tmp/mpi_host_file', slot_pattern=':'):
        self.nb_nodes = int(number_of_nodes)
        self.slots = int(number_of_cpu)
        self.hostfile_path = hostfile_path
        self.slot_pattern = slot_pattern # MPICH ":" | OpenMPI " slots="

    def run(self, nodes, master, user, user_shell, volumes):
        nodeList = []
        for i in range(1, self.nb_nodes):
            nodeList.append("node%03d" % i)

        # Create Hostfile
        master.ssh.execute("echo master%s%d > %s" % (self.slot_pattern, self.slots, self.hostfile_path))
        for node in nodeList:
            master.ssh.execute("echo %s%s%d >> %s" % (node, self.slot_pattern, self.slots, self.hostfile_path))

        # Create Max Process File
        master.ssh.execute("echo %d > %s" % (self.slots * self.nb_nodes, self.hostfile_path + '.size'))

class StartX(ClusterSetup):
    def run(self, nodes, master, user, user_shell, volumes):
        sudoCmd = 'sudo '
        if user == 'root':
            sudoCmd = ''
        for node in nodes:
            log.debug('run on %s: %s' % (node.alias, ("%sX :0 &" % sudoCmd)))
            node.ssh.execute("%sX :0 &" % sudoCmd)
            log.debug('run on %s: OK' % node.alias)
