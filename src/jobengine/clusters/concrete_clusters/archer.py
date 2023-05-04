import logging

import paramiko

from jobengine import job
from jobengine.clusters.abstract_clusters.pbs_cluster import PBSCluster


class Archer(PBSCluster):
    name = "ARCHER"
    proxy = None
    hostname = "archer"
    username = "jandom"
    path = "/home/e460/e460/jandom"
    partitions = {"standard", "short", "long", "low", "serial"}

    def launch(
        self, shell: paramiko.SSHClient, job: job.Job, /, **kwargs
    ) -> tuple[list[str], list[str]]:
        nodes = kwargs.get("nodes", job.nodes)
        partition = kwargs.get("partition", job.partition)
        default_duration = "48:00:00" if partition == "long" else "24:00:00"
        duration = kwargs.get("duration", default_duration)
        jobname = kwargs.get("jobname", job.name)

        logging.debug(f"{nodes=}")
        # http://www.pbsworks.com/documentation/support/PBSProUserGuide11.2.pdf
        # Page 42, Table 3-1
        cmd = "cd {directory}; qsub -A e460 -q {queue} -l select={nodes}:ncpus=24 -l place=scatter:excl -l walltime={walltime} -N {jobname} submit.sh".format(
            directory=job.remote_workdir,
            queue=partition,
            nodes=nodes,
            walltime=duration,
            jobname=jobname,
        )
        logging.debug(f"{cmd=}")
        stdout, stderr = self.run_shell_command(cmd)
        return stdout, stderr
