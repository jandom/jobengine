import logging

import paramiko

from jobengine import job
from jobengine.clusters.abstract_clusters.slurm_cluster import SlurmCluster


class ArcusB(SlurmCluster):
    name = "ARCUS-B"
    proxy = None
    hostname = "arcus-b"
    username = "jdomanski"
    path = "/home/sbcb-membr/jdomanski/"
    partitions = {"compute"}

    def launch(
        self, shell: paramiko.SSHClient, job: job.Job, /, **kwargs
    ) -> tuple[list[str], list[str]]:
        partition = kwargs.get("partition", job.partition)
        jobname = kwargs.get("jobname", job.name)
        nodes = kwargs.get("nodes", job.nodes)
        ntasks = kwargs.get("ntasks_per_node", 16)
        duration = kwargs.get("duration", "24:00:00")

        cmd = "cd {directory}; {submit_command} --partition={partition} --job-name={jobname}  --nodes={nodes} {flags} --ntasks-per-node={ntasks} --time={time} {directory}/submit.sh".format(
            directory=job.remote_workdir,
            submit_command=self.submit_command,
            partition=partition,
            jobname=jobname,
            nodes=nodes,
            flags="--exclusive",
            ntasks=ntasks,
            time=duration,
        )

        logging.debug(f"{cmd=}")
        stdout, stderr = self.run_shell_command(cmd)
        return stdout, stderr

    def submit(self, job: job.Job, /, **kwargs) -> None:
        shell = self.get_shell()
        out, err = self.launch(shell, job, **kwargs)
        print((out, err))
        cluster_id = int(out[0].split()[-1])
        job.cluster_id = cluster_id
        print(cluster_id)
        job.status = self.get_status(job)
        print((job.status))
