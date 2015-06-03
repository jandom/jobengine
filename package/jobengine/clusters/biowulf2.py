

from slurmcluster import SlurmCluster
import spur
class Biowulf2(SlurmCluster):
    name = "BIOWULF2"
    proxy = None
    hostname = "helix.nih.gov"
    username = "domanskij"
    path = "/data/domanskij"
        
    def get_status(self, shell, job):
        if not job.cluster_id: return None
        cmd = "{} {}".format(self.status_command, job.cluster_id)
        print cmd
        (stdin, stdout, stderr) = shell.exec_command(cmd)
        stdout, stderr = stdout.readlines(), stderr.readlines()
        #print stdout, stderr
        assert(len(stderr) == 0), stderr
        assert(len(stdout) == 2), stdout
        st = stdout[1].split()[4]
        return st
      
    def do_submit(self, shell, remote_workdir,  **kwargs):
        (stdin, stdout, stderr) = shell.exec_command("cd {}; {} --partition=norm --job-name=gmx  --nodes={} --exclusive --ntasks-per-node=16  --time={} {}/submit.sh".format(remote_workdir, self.submit_command, kwargs.get('nodes', 1), kwargs.get('duration', '24:00:00'), remote_workdir))  
        return stdout.readlines(), stderr.readlines()
        
    def submit(self, shell, job, **kwargs):        
        kwargs["nodes"] = job.nodes 
        out, err = self.do_submit(shell, job.remote_workdir, **kwargs)
        
        cluster_id = int(out[0])
        job.cluster_id = cluster_id
        print cluster_id
        job.status = self.get_status(shell, job)
        print job.status
        return job
        
    def cancel(self, shell, job):
        status = self.get_status(shell, job)
        (stdin, stdout, stderr) = shell.exec_command("{} {}".format(self.cancel_command, job.cluster_id))
        stdout, stderr = stdout.readlines(), stderr.readlines()
        print stdout, stderr
        return True

