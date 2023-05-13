import logging
import random

import paramiko

from jobengine import job
from jobengine.clusters.abstract_clusters.slurm_cluster import SlurmCluster


def generate_flags(partition: str, /) -> str:
    constraint = (
        "--constraint=x2695"
        if random.random() > 5989.0 / (5989 + 23632)
        else "--constraint=x2650"
    )
    if partition != "multinode":
        constraint = ""
    return constraint + " --exclusive"


class Biowulf2(SlurmCluster):
    name = "BIOWULF2"
    hostname = "helix.nih.gov"
    username = "domanskij"
    path = "/data/domanskij"
    partitions = {"norm", "multinode", "niddk"}

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
            flags=generate_flags(partition),
            ntasks=ntasks,
            time=duration,
        )

        logging.debug(cmd)
        stdout, stderr = self.run_shell_command(cmd)
        return stdout, stderr

    def submit(self, job: job.Job, /, **kwargs) -> None:
        shell = self.get_shell()
        # submit the job
        out, err = self.launch(shell, job, **kwargs)
        logging.debug((out, err))

        # get cluster id
        cluster_id = int(out[0])
        job.cluster_id = cluster_id
        logging.debug(cluster_id)

        # check job status
        job.status = self.get_status(job)
        logging.debug((job.status))
