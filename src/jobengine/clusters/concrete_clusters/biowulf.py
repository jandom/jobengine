import logging

import paramiko

from jobengine.clusters.abstract_clusters.pbs_cluster import PBSCluster
from jobengine.model import job
from jobengine.status import Status


def parse_biowulf_cluster_id(lines: list[str]) -> int:
    assert len(lines) == 1
    cluster_id = int(lines[0].split(".biobos")[0])
    return cluster_id


def parse_biowulf_status(job: job.Job, stdout: list[str], stderr: list[str], /) -> str:
    if len(stderr) and "Unknown Job Id" in stderr[0]:
        job.status = Status.Cancelled
        return Status.Cancelled
    assert len(stdout) == 3
    status_code = stdout[-1].split()[-2]
    return status_code


class Biowulf(PBSCluster):
    """
    Access to biowulf is much more contrived then others - we're using its definition
    from the ~/.ssh/config which includes a ProxyCommand
    """

    name = "BIOWULF"
    hostname = "helix.nih.gov"
    username = "domanskij"
    path = "/data/domanskij"
    status_all_command = "/usr/local/pbs/bin/qstat -u {}".format(username)

    def cancel(self, job: job.Job, /) -> None:
        status = self.get_status(job)
        if status == Status.Running:
            cmd = "/usr/local/pbs/bin/qdel {}".format(str(job.cluster_id))
            logging.debug(cmd)
            stdout, stderr = self.run_shell_command(cmd)
            logging.debug((stdout, stderr))

    def get_status(self, job: job.Job, /) -> Status:
        cmd = "/usr/local/pbs/bin/qstat {cluster_id}.biobos".format(
            cluster_id=job.cluster_id
        )
        stdout, stderr = self.run_shell_command(cmd)
        status_code = parse_biowulf_status(job, stdout, stderr)
        return Status[status_code]

    def launch(
        self, shell: paramiko.SSHClient, job: job.Job, /, **kwargs
    ) -> tuple[list[str], list[str]]:
        nodes = kwargs.get("nodes", job.nodes)
        duration = kwargs.get("duration", "24:00:00")
        cmd = "cd {directory}; /usr/local/pbs/bin/qsub -q lcp -l nodes={nodes},walltime={walltime} submit.sh".format(
            directory=job.remote_workdir,
            nodes=nodes,
            walltime=duration,
        )
        stdout, stderr = self.run_shell_command(cmd)
        return stdout, stderr

    def submit(self, job: job.Job, /, **kwargs) -> None:
        shell = self.get_shell()
        stdout, stderr = self.launch(shell, job, **kwargs)
        logging.debug((stdout, stderr))
        cluster_id = parse_biowulf_cluster_id(stdout)
        job.cluster_id = cluster_id
        job.status = self.get_status(job)
