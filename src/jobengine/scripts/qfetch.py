#!/usr/bin/env python

import argparse
import logging

from sqlalchemy import create_engine

# sqlalchemy
from sqlalchemy.orm import Session, sessionmaker

from jobengine.clusters.cluster_registry import cluster_registry
from jobengine.configuration import create_configuration
from jobengine.controller.get import get_job_from_workdir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", "-w", default=["workdir"], nargs="+")
    return parser.parse_args()


def fetch(session: Session, workdir: str, /):
    job = get_job_from_workdir(session=session, workdir=workdir)
    logging.debug((job.status, job.name, job.id, job.workdir))
    cluster = cluster_registry.get_cluster(job.cluster_name)
    cluster.pull(job)


def main():
    args = parse_args()
    config = create_configuration()
    engine = create_engine(config.engine_file)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        for workdir in args.workdir:
            fetch(session=session, workdir=workdir)


if __name__ == "__main__":
    main()
