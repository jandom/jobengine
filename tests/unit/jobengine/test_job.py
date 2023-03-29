import uuid

from jobengine.job import Job
from jobengine.status import Status


def test_constructor():
    uuid0 = str(uuid.uuid4())
    job = Job(
        name="test-job",
        uuid=uuid,
        workdir="/tmp/test-job",
        local_workdir=f"/tmp/.lockers/{uuid0}",
        remote_workdir=f"/data/username/.lockers/{uuid0}",
        cluster_name="test-cluster",
        cluster_id=1,
    )
    assert job.status == Status.Unknown
