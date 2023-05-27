#!/usr/bin/env python

import argparse
import logging
import os

from sqlalchemy import session

from jobengine.clusters.cluster_registry import cluster_registry
from jobengine.configuration import create_session
from jobengine.controller.create import create_job
from jobengine.controller.get import get_job_from_workdir
from jobengine.status import Status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--job_name")
    parser.add_argument("-c", "--cluster")
    parser.add_argument("-p", "--partition")

    parser.add_argument("--workdir", "-w", nargs="*", default=[])
    parser.add_argument("--duration", "-d", default="24:00:00")
    parser.add_argument("--nodes", "-n", type=int)
    parser.add_argument("--ntasks-per-node", type=int, default=16)
    parser.add_argument("--processes", type=int, default=16)
    args = parser.parse_args()
    # automatically add 'workdir' if it exists
    if args.workdir == [] and os.path.exists("workdir"):
        args.workdir = ["workdir"]
    return args


def resubmit_workdir(
    *, args: argparse.Namespace, session: session.Session, workdir: str
) -> None:
    job = get_job_from_workdir(session=session, workdir=workdir)
    logging.info(job)
    if job.status in {Status.Running, Status.Queued, Status.Pending}:
        logging.info("Job already running or queued")
        return
    cluster = cluster_registry.get_cluster(job.cluster_name)
    cluster.submit(
        job,
        duration=args.duration,
        nodes=args.nodes,
        partition=args.partition,
        ntasks_per_node=args.ntasks_per_node,
    )
    status = cluster.get_status(job)
    job.status = status

    # update partition and nodes, if needed
    if args.partition and job.partition != args.partition:
        job.partition = args.partition
    if args.nodes and job.nodes != args.nodes:
        job.nodes = args.nodes

    session.add(job)
    session.commit()


def create_workdir(*, args: argparse.Namespace, session: session.Session) -> None:
    cluster = cluster_registry.get_cluster(args.cluster)
    job = create_job(
        cluster=cluster,
        job_name=args.job_name,
        nodes=args.nodes,
        processes=args.processes,
        partition=args.partition,
    )
    assert job
    status = cluster.get_status(job)
    logging.info((job, status))
    if job.cluster_id == 0:
        cluster.submit(job)
    session.add(job)
    session.commit()


def main() -> None:
    args = parse_args()

    with create_session() as session:
        # Re-submit existing workdirs
        if len(args.workdir) > 0:
            for workdir in args.workdir:
                resubmit_workdir(args=args, session=session, workdir=workdir)
        # Create a brand-new workdir
        else:
            create_workdir(args=args, session=session)


if __name__ == "__main__":
    main()
