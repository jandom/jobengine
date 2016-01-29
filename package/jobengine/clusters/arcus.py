
from pbscluster import PBSCluster
    
class Arcus(PBSCluster):
    name = "ARCUS"
    proxy = None
    hostname = "arcus"
    username = "jdomanski"
    path = "/home/sbcb-membr/jdomanski/"

    def do_submit(self, shell, job, **kwargs):
        
        nodes = kwargs.get('nodes', job.nodes)
        duration = kwargs.get('duration', '24:00:00')
        jobname = kwargs.get('jobname', job.name)
        print "nodes=", nodes

        (stdin, stdout, stderr) = shell.exec_command("cd {}; qsub -l nodes={}:ppn=16 -l walltime={} -N {} submit.sh".format(job.remote_workdir, nodes, duration, jobname))
        return stdout    