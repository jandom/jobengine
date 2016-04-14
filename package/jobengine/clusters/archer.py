
from pbscluster import PBSCluster

class Archer(PBSCluster):
    name = "ARCHER"
    proxy = None
    hostname = "archer"
    username = "jandom"
    path = "/home/e460/e460/jandom"
    partitions = ["standard", "short"]

    def do_submit(self, shell, job, **kwargs):

        nodes = kwargs.get('nodes') if kwargs.get('nodes') else job.nodes
        duration = kwargs.get('duration') if kwargs.get('duration') else '24:00:00'
        jobname = kwargs.get('jobname') if kwargs.get('jobname') else job.name
        print "nodes=", nodes
        cmd = "cd {}; qsub -q {} -l select={} -l walltime={} -N {} submit.sh".format(job.remote_workdir, job.partition, nodes, duration, jobname)
        print("cmd=",cmd)
        (stdin, stdout, stderr) = shell.exec_command(cmd)
        return stdout, stderr
