from jobengine.clusters.abstract_clusters import slurm_cluster
from jobengine.status import Status


def test_parse_slurm_status():
    stdout = []
    stderr = ["fake-error"]
    status = slurm_cluster.parse_slurm_status(stdout, stderr)
    assert status == Status.Cancelled
