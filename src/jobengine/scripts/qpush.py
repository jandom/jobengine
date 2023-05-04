#!/usr/bin/env python

import argparse
import logging

from sqlalchemy import create_engine

# sqlalchemy
from sqlalchemy.orm import sessionmaker

from jobengine.clusters.cluster_registry import cluster_registry
from jobengine.configuration import create_configuration

# jobengire
from jobengine.controller.get import get_job_from_workdir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", default="workdir")
    return parser.parse_args()


def main():
    args = parse_args()
    config = create_configuration()
    engine = create_engine(config.engine_file)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        job = get_job_from_workdir(session, args.workdir)
        cluster, shell = cluster_registry.get_cluster(job.cluster_name)
        logging.info((cluster, shell))
        cluster.push(shell, job)


if __name__ == "__main__":
    main()
