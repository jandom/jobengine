#!/usr/bin/env python

import argparse
import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jobengine.clusters.cluster_registry import cluster_registry
from jobengine.configuration import create_configuration
from jobengine.controller.create import create_job
from jobengine.controller.get import get_job_from_workdir
from jobengine.job import Job
from jobengine.status import Status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--topol", default="topol.tpr")
    parser.add_argument("-j", "--jobname")
    parser.add_argument("-c", "--cluster")
    parser.add_argument("-p", "--partition")

    parser.add_argument("--workdir", "-w", nargs="*", default=[])
    parser.add_argument("--duration", "-d", default="24:00:00")
    parser.add_argument("-n", "--nodes", type=int)
    parser.add_argument("--ntasks-per-node", type=int, default=16)
    parser.add_argument("--processes", type=int, default=16)
    parser.add_argument("-s", "--script")
    args = parser.parse_args()
    # automatically add 'workdir' if it exists
    if args.workdir == [] and os.path.exists("workdir"):
        args.workdir = ["workdir"]
    return args


def main() -> None:
    args = parse_args()

    config = create_configuration()
    engine = create_engine(config.engine_file)
    Job.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    with Session() as session:
        # Restore an existing workdir
        if len(args.workdir):
            for workdir in args.workdir:
                job = get_job_from_workdir(session=session, workdir=workdir)
                logging.info(job)
                if job.status in {Status.Running, Status.Queued, Status.Pending}:
                    logging.info("Job already running or queued")
                    continue
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

                if args.partition and job.partition != args.partition:
                    job.partition = args.partition
                if args.nodes and job.nodes != args.nodes:
                    job.nodes = args.nodes

                session.add(job)
                session.commit()
        # Create a brand-new workdir
        else:
            cluster = cluster_registry.get_cluster(args.cluster)
            job = create_job(
                args.topol,
                cluster=cluster,
                job_name=args.jobname,
                duration=args.duration,
                nodes=args.nodes,
                processes=args.processes,
                partition=args.partition,
                ntasks_per_node=args.ntasks_per_node,
            )
            assert job
            status = cluster.get_status(job)
            logging.info((job, status))
            if job.cluster_id == 0:
                cluster.submit(job)
            session.add(job)
            session.commit()


if __name__ == "__main__":
    main()
