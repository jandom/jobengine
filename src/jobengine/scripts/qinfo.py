#!/usr/bin/env python

import argparse
import logging

from jobengine.clusters.cluster_registry import cluster_registry
from jobengine.configuration import create_session

# jobengire
from jobengine.controller.get import get_job_from_workdir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", "-w", default=["workdir"], nargs="+")
    parser.add_argument("--refresh", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    with create_session() as session:
        for workdir in args.workdir:
            job = get_job_from_workdir(session, workdir)
            logging.info((workdir, job))

            if not args.refresh:
                continue

            cluster = cluster_registry.get_cluster(job.cluster_name)
            logging.info(cluster)
            actual, desired = job.status, cluster.get_status(job)
            logging.info("actual =", actual, "desired =", desired)
            if actual == desired:
                continue

            logging.info("Updating")
            job.status = desired
            session.add(job)
            session.commit()


if __name__ == "__main__":
    main()
