import logging

import paramiko

from jobengine import job
from jobengine.clusters.abstract_clusters.pbs_cluster import PBSCluster


class Arcus(PBSCluster):
    name = "ARCUS"
    proxy = None
    hostname = "arcus"
    username = "jdomanski"
    path = "/home/sbcb-membr/jdomanski/"

    def launch(
        self, shell: paramiko.SSHClient, job: job.Job, /, **kwargs
    ) -> tuple[list[str], list[str]]:
        nodes = kwargs.get("nodes", job.nodes)
        duration = kwargs.get("duration", "24:00:00")
        jobname = kwargs.get("jobname", job.name)
        logging.debug(f"{nodes=}")

        cmd = "cd {directory}; qsub -l nodes={nodes}:ppn=16 -l walltime={walltime} -N {jobname} submit.sh".format(
            directory=job.remote_workdir,
            nodes=nodes,
            walltime=duration,
            jobname=jobname,
        )
        stdout, stderr = self.run_shell_command(cmd)
        return stdout, stderr
