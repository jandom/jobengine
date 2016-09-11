
from pbscluster import PBSCluster

class Archer(PBSCluster):
    name = "ARCHER"
    proxy = None
    hostname = "archer"
    username = "jandom"
    path = "/home/e460/e460/jandom"
    partitions = ["standard", "short", "long", "low", "serial"]

    def do_submit(self, shell, job, **kwargs):

        nodes = kwargs.get('nodes') if kwargs.get('nodes') else job.nodes
        duration = kwargs.get('duration') if kwargs.get('duration') else '24:00:00'
        jobname = kwargs.get('jobname') if kwargs.get('jobname') else job.name
        partition = kwargs.get('partition') if kwargs.get('partition') else job.partition
        print "nodes=", nodes
	# http://www.pbsworks.com/documentation/support/PBSProUserGuide11.2.pdf
	# Page 42, Table 3-1
        cmd = "cd {}; qsub -A e460 -q {} -l select={}:ncpus=24 -l place=scatter:excl -l walltime={} -N {} submit.sh".format(job.remote_workdir, partition, nodes, duration, jobname)
        print("cmd=",cmd)
        (stdin, stdout, stderr) = shell.exec_command(cmd)
        return stdout, stderr
