
from base import Cluster

class PBSCluster(Cluster):
    status_command = "qstat -x"
    status_all_command = "qstat"
    submit_command = "qsub"
    cancel_command = "qdel"

    def parse_qsub(self, stdout, stderr):
        lines = stderr.readlines()
        print("stderr=", lines)
        assert(len(lines)==0)

        lines = stdout.readlines()
        print("stdout=", lines)
        assert(len(lines)==1)

        cluster_id = int(lines[0].split(".")[0])
        return cluster_id

    def get_status(self, shell, job):
        (stdin, stdout, stderr) = shell.exec_command("qstat {}".format(job.cluster_id))
        stdout = stdout.readlines()
        stderr = stderr.readlines()

        if len(stderr):
            print("stderr=", stderr[0])
            job.status = "C"
            return "C"
        #print stdout, stderr
        assert(len(stdout)==3)
        status_code = stdout[-1].split()[-2]
        return str(status_code)

    def do_submit(self, shell, remote_workdir, **kwargs):
        print kwargs.get('nodes', 1)
        (stdin, stdout, stderr) = shell.exec_command("cd {}; qsub submit.sh".format(remote_workdir))
        return stdout, stderr

    def submit(self, shell, job, **kwargs):
        stdout, stderr = self.do_submit(shell, job, **kwargs)
        cluster_id = self.parse_qsub(stdout, stderr)
        job.cluster_id = cluster_id
        job.status = self.get_status(shell, job)
        return job

    def cancel(self, shell, job):
        status = self.get_status(shell, job)

        # if job is running or queue
        if status in ["R", "Q"]:
            cmd = "qdel {}".format(str(job.cluster_id))
            print(cmd)
            (stdin, stdout, stderr) = shell.exec_command(cmd)
            stdout = stdout.readlines()
            stderr = stderr.readlines()
            if stdout:
                return False
        else:
            print("Not cancelling - job status is {} (should be R or Q to cancel)".format(status))
        return True
