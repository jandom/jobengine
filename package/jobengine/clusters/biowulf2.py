

from slurmcluster import SlurmCluster
import spur
class Biowulf2(SlurmCluster):
    name = "BIOWULF2"
    proxy = None
    hostname = "helix.nih.gov"
    username = "domanskij"
    path = "/data/domanskij"
    partition = "norm"

    def do_submit(self, shell, job,  **kwargs):
        cmd = "cd {}; {} --partition={} --job-name={}  --nodes={} --exclusive --ntasks-per-node=16  --time={} {}/submit.sh".format(
                job.remote_workdir, 
                self.submit_command, 
                self.partition, 
                kwargs.get('jobname', job.name), 
                kwargs.get('nodes', job.nodes), 
                kwargs.get('duration', '24:00:00'), 
                job.remote_workdir
            )

        (stdin, stdout, stderr) = shell.exec_command(cmd)  
        return stdout.readlines(), stderr.readlines()
        
    def submit(self, shell, job, **kwargs):        

        out, err = self.do_submit(shell, job, **kwargs)        
        print out, err
        cluster_id = int(out[0])
        job.cluster_id = cluster_id
        print cluster_id
        job.status = self.get_status(shell, job)
        print job.status
        return job
        

