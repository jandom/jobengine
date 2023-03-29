import logging

from jobengine import job
from jobengine.clusters.abstract_clusters.base_cluster import BaseCluster
from jobengine.status import Status


def parse_slurm_status(stdout: list[str], stderr: list[str], /) -> Status:
    if len(stderr) > 0 or len(stdout) == 1:
        return Status.Cancelled
    assert len(stdout) == 2, stdout
    status = stdout[1].split()[4]
    return Status[status]


class SlurmCluster(BaseCluster):
    status_command = "squeue --job"
    submit_command = "sbatch"
    cancel_command = "scancel"

    def get_status(self, job: job.Job, /) -> Status:
        cmd = "{} {}".format(self.status_command, job.cluster_id)
        stdout, stderr = self.run_shell_command(cmd)
        return parse_slurm_status(stdout, stderr)

    def cancel(self, job: job.Job, /) -> None:
        cmd = "{} {}".format(self.cancel_command, job.cluster_id)
        stdout, stderr = self.run_shell_command(cmd)
        logging.debug(("stdout=", stdout, "stderr=", stderr))
