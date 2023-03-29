#!/usr/bin/env python

import argparse
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jobengine.clusters.cluster_registry import cluster_registry
from jobengine.configuration import create_configuration
from jobengine.controller.get import get_job_from_workdir
from jobengine.status import Status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", "-w", default=["workdir"], nargs="+")
    parser.add_argument(
        "--dry",
        "-d",
        action="store_true",
        help="Mark as cancelled in the database, but don't actually kill the job on the cluster",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config = create_configuration()
    engine = create_engine(config.engine_file)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        for workdir in args.workdir:
            logging.info(workdir)
            job = get_job_from_workdir(session=session, workdir=workdir)
            cluster = cluster_registry.get_cluster(job.cluster_name)
            if args.dry:
                continue
            cluster.cancel(job)
            job.status = Status.Cancelled
            session.add(job)
            session.commit()


if __name__ == "__main__":
    main()
