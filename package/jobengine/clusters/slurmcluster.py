
from base import Cluster
import spur

class SlurmCluster(Cluster):
    status_command = "squeue --job"
    submit_command = "sbatch"
    cancel_command = "scancel"

    def get_status(self, shell, job):
        if not job.cluster_id: return None
        cmd = "{} {}".format(self.status_command, job.cluster_id)
        print("cmd=",cmd)
        (stdin, stdout, stderr) = shell.exec_command(cmd)
        stdout, stderr = stdout.readlines(), stderr.readlines()
        
        #assert(len(stderr) == 0), stderr
	if (len(stderr) > 0): return "C"
        assert(len(stdout) == 2), stdout
        st = stdout[1].split()[4]
        return st    
        
    def cancel(self, shell, job):
        #status = self.get_status(shell, job)
        (stdin, stdout, stderr) = shell.exec_command("{} {}".format(self.cancel_command, job.cluster_id))
        stdout, stderr = stdout.readlines(), stderr.readlines()
        print("stdout=",stdout, "stderr=",stderr)
        return True
