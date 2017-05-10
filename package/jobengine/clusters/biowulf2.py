
from slurmcluster import SlurmCluster
import random

class Biowulf2(SlurmCluster):
    name = "BIOWULF2"
    proxy = None
    hostname = "helix.nih.gov"
    username = "domanskij"
    path = "/data/domanskij"
    partitions = ["norm", "multinode", "niddk"]


    def do_submit(self, shell, job,  **kwargs):

        partition = kwargs.get('partition') if kwargs.get('partition') else job.partition
        jobname   = kwargs.get('jobname') if kwargs.get('jobname') else job.name
        nodes     = kwargs.get('nodes') if kwargs.get('nodes') else job.nodes
        ntasks    = kwargs.get("ntasks_per_node") if kwargs.get("ntasks_per_node") else 16
        duration  = kwargs.get('duration') if kwargs.get('duration') else '24:00:00'

	constraint = "--constraint=x2695" if random.random() > 5989./(5989+23632) else "--constraint=x2650"
	if partition is not "multinode": constraint = ""
        cmd = "cd {}; {} --partition={} {} --job-name={}  --nodes={} {} --ntasks-per-node={} --time={} {}/submit.sh".format(
                job.remote_workdir,
                self.submit_command,
                partition,
		constraint,
                jobname,
                nodes,
                "--exclusive", # if kwargs.get('ntasks_per_node', 16) == 16 else "",
                ntasks,
                duration,
                job.remote_workdir
            )

        print(cmd)
        (stdin, stdout, stderr) = shell.exec_command(cmd)
        return stdout.readlines(), stderr.readlines()

    def submit(self, shell, job, **kwargs):

	# submit the job
        out, err = self.do_submit(shell, job, **kwargs)
        print out, err

	# get cluster id
        cluster_id = int(out[0])
        job.cluster_id = cluster_id
        print cluster_id

	# check job status
        job.status = self.get_status(shell, job)
        print job.status
        return job

