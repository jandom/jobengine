import logging
import os
import shutil
import uuid

from scp import SCPClient, SCPException

from jobengine import configuration
from jobengine.clusters.abstract_clusters.base_cluster import BaseCluster as Cluster
from jobengine.model import job

ignore = shutil.ignore_patterns("#*", "workdir*", "analysis*", "test*", "trash*")


def create_local_workdir(
    *, lockers_directory: str, local_dir: str, identifier: str
) -> str:
    assert not os.path.exists("workdir")
    workdir_directory = "%s/%s" % (lockers_directory, identifier)
    logging.info(f"local copy src={local_dir} dst={workdir_directory}")
    shutil.copytree(local_dir, workdir_directory, symlinks=False, ignore=ignore)
    os.symlink(workdir_directory, "workdir")
    return workdir_directory


def copy_local_workdir_to_remote(*, cluster: Cluster, local_workdir: str):
    dst = "%s/.lockers/" % (cluster.path)
    logging.info(f"remote copy: src={local_workdir} dst={cluster.name}")
    scp = SCPClient(cluster.get_shell().get_transport(), socket_timeout=600)
    try:
        scp.put(local_workdir, dst, recursive=True)
    except SCPException as e:
        logging.error(f"SCPException {e=}")
        shutil.rmtree(local_workdir)
        os.remove("workdir")
        raise e


def create_job(
    *,
    cluster: Cluster,
    partition: str,
    job_name: str = "workdir",
    nodes: int = 1,
    processes: int = 16,
) -> job.Job:
    config = configuration.create_configuration()
    identifier = str(uuid.uuid4())
    local_dir = os.getcwd()

    local_workdir = create_local_workdir(
        lockers_directory=config.lockers_directory,
        identifier=identifier,
        local_dir=local_dir,
    )

    copy_local_workdir_to_remote(cluster=cluster, local_workdir=local_workdir)

    logging.info(f"{nodes=} {processes=} {identifier=} {partition=}")

    return job.Job(
        name=job_name,
        uuid=identifier,
        workdir=local_workdir,
        local_workdir=local_dir,
        remote_workdir="%s/.lockers/%s" % (cluster.path, identifier),
        cluster_name=cluster.name,
        cluster_id=0,
        nodes=nodes,
        partition=partition,
    )
