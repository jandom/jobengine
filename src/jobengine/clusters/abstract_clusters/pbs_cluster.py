import logging

import paramiko

from jobengine.clusters.abstract_clusters.base_cluster import BaseCluster
from jobengine.model import job
from jobengine.status import Status


def parse_pbs_cluster_id(stdout: list[str], stderr: list[str], /) -> int:
    assert len(stderr) == 0
    assert len(stdout) == 1
    [identifier] = stdout
    cluster_id, _ = identifier.split(".")
    return int(cluster_id)


def parse_pbs_status(stdout: list[str], /) -> str:
    assert len(stdout) == 3
    status_code = stdout[-1].split()[-2]
    return status_code


class PBSCluster(BaseCluster):
    status_command = "qstat -x"
    status_all_command = "qstat"
    submit_command = "qsub"
    cancel_command = "qdel"

    def get_status(self, job: job.Job, /) -> Status:
        cmd = "qstat {}".format(job.cluster_id)
        stdout, _ = self.run_shell_command(cmd)
        status = parse_pbs_status(stdout)
        return Status[status]

    def launch(
        self, shell: paramiko.SSHClient, job: job.Job, /, **kwargs
    ) -> tuple[list[str], list[str]]:
        cmd = "cd {}; qsub submit.sh".format(job.remote_workdir)
        stdout, stderr = self.run_shell_command(cmd)
        return stdout, stderr

    def submit(self, job: job.Job, /, **kwargs) -> None:
        shell = self.get_shell()
        stdout, stderr = self.launch(shell, job, **kwargs)
        cluster_id = parse_pbs_cluster_id(stdout, stderr)
        job.cluster_id = cluster_id
        job.status = self.get_status(job)

    def cancel(self, job: job.Job, /) -> None:
        status = self.get_status(job)

        # if job is running or queue
        if status in {Status.Running, Status.Queued}:
            cmd = "qdel {}".format(str(job.cluster_id))
            logging.debug(cmd)
            _, _ = self.run_shell_command(cmd)
        else:
            logging.debug(
                (
                    "Not cancelling - job status is {} (should be R or Q to cancel)".format(
                        status
                    )
                )
            )
