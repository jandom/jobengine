#!/usr/bin/env python

import argparse
import logging

from jobengine.clusters.cluster_registry import cluster_registry
from jobengine.configuration import create_session

# jobengire
from jobengine.controller.get import get_job_from_workdir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", default="workdir")
    return parser.parse_args()


def main():
    args = parse_args()
    with create_session() as session:
        job = get_job_from_workdir(session, args.workdir)
        cluster = cluster_registry.get_cluster(job.cluster_name)
        logging.info(job)
        logging.info(cluster)
        cluster.delete(job)


if __name__ == "__main__":
    main()
