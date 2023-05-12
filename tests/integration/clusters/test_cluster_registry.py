import hashlib
import pathlib
import shutil

from jobengine.job import Job
from tests.integration.helpers import create_cluster_registry

EXAMPLE_CLUSTER_NAMES = [
    "localhost",
]


def create_test_job(uuid: str, remote_workdir: str, local_workdir: str):
    return Job(
        name="fake-name",
        uuid=uuid,
        workdir="fake-workdir",
        local_workdir=local_workdir,
        remote_workdir=remote_workdir,
        cluster_name="localhost",
        cluster_id=1,
    )


def md5sum(filepath: str) -> str:
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def test_get_cluster():
    cluster_registry = create_cluster_registry()
    for cluster_name in EXAMPLE_CLUSTER_NAMES:
        cluster = cluster_registry.get_cluster(cluster_name)
        cluster.run_shell_command("echo 'hello world'")


def test_rsync_push(tmp_path_factory):
    source = tmp_path_factory.mktemp("source") / ".lockers" / "fake-uuid"
    destination = tmp_path_factory.mktemp("destination") / ".lockers" / "fake-uuid"
    source.mkdir(parents=True)
    destination.mkdir(parents=True)

    input_tpr_filename = (
        pathlib.Path(__file__).parent.parent
        / "data"
        / "M2__monomer__charmm36__charmm22stprot__tip3p__strand_bilayer__run_1.tpr"
    )
    shutil.copy(input_tpr_filename, source / "topol.tpr")
    job = create_test_job(
        uuid="fake-uuid",
        local_workdir=str(source.parent.parent),
        remote_workdir=str(destination.parent.parent),
    )
    cluster_registry = create_cluster_registry()
    for cluster_name in EXAMPLE_CLUSTER_NAMES:
        cluster = cluster_registry.get_cluster(cluster_name)
        import subprocess

        print(subprocess.check_output(["ls", "-l", str(source)]))
        cluster.push(job)
        desired = md5sum(source / "topol.tpr")
        actual = md5sum(destination / "topol.tpr")
        assert actual == desired
