import os
import shutil
import uuid

from scp import SCPClient, SCPException

from jobengine import configuration, job
from jobengine.clusters.abstract_clusters.base_cluster import BaseCluster as Cluster


def create_job(
    tpr,
    /,
    *,
    cluster: Cluster,
    job_name="workdir",
    duration="24:00:00",
    nodes=1,
    processes=16,
    partition=None,
    ntasks_per_node=16,
) -> job.Job:
    config = configuration.create_configuration()

    # Create workdir, copy files over there
    assert not os.path.exists("workdir")
    id0 = str(uuid.uuid4())
    workdir = "%s/%s" % (config.lockers_directory, id0)

    local_dir = os.getcwd()
    ignore = shutil.ignore_patterns("#*", "workdir*", "analysis*", "test*", "trash*")
    print(("local copy:", "src=", local_dir, "dst=", workdir))
    shutil.copytree(local_dir, workdir, symlinks=False, ignore=ignore)
    os.symlink(workdir, "workdir")

    # Setup SSH client to copy files over via scp
    dst = "%s/.lockers/" % (cluster.path)
    print(
        (
            "remote copy:",
            "src=",
            workdir,
            "dst=",
            cluster.name,
            ":",
        )
    )
    scp = SCPClient(cluster.get_shell().get_transport(), socket_timeout=600)
    try:
        scp.put(workdir, dst, recursive=True)
    except SCPException as e:
        print(("SCPException", e))
        shutil.rmtree(workdir)
        os.remove("workdir")
        raise e

    remote_workdir = "%s/.lockers/%s" % (cluster.path, id0)

    # if not partition: cluster.partitions[0]

    print(
        ("nodes=", nodes, "processes=", processes, "id=", id0, "partition=", partition)
    )

    cluster_id = 0
    return job.Job(
        name=job_name,
        uuid=id0,
        workdir=workdir,
        local_workdir=local_dir,
        remote_workdir=remote_workdir,
        cluster_name=cluster.name,
        cluster_id=cluster_id,
        nodes=nodes,
        partition=partition,
    )
