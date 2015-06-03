
from base import Cluster
import spur

class SlurmCluster(Cluster):
    status_command = "squeue --job"
    submit_command = "sbatch"
    cancel_command = "scancel"
     
    def do_submit(self, shell, remote_workdir,  **kwargs):
        (stdin, stdout, stderr) = shell.exec_command("cd {}; sbatch {}/submit.sh".format(remote_workdir, remote_workdir))  
        return stdout.readlines(), stderr.readlines()
        
    def cancel(self, shell, job):
        status = self.get_status(shell, job)
        if status == "R" or status == "PD": # slurm status codes: Running and Pending
          (stdin, stdout, stderr) = shell.exec_command("scancel {}".format(str(job.cluster_id)))
          if stdout.readlines():
            return False 
        return True
