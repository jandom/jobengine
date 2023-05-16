#!/usr/bin/env python
import argparse
import fcntl
import logging
import os

from sqlalchemy import create_engine

# sqlalchemy
from sqlalchemy.orm import Session, sessionmaker

from jobengine.clusters.cluster_registry import cluster_registry
from jobengine.configuration import create_configuration
from jobengine.model.job import Job
from jobengine.status import Status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", default="resubmit")
    parser.add_argument("--clusters", nargs="*", default=["biowulf"])
    return parser.parse_args()


def process_resubmit(session: Session, args: argparse.Namespace, /) -> None:
    logging.info("Checking")
    jobs = [
        job
        for job in session.query(Job).order_by(Job.id)
        if job.status != Status.Stopped
    ]
    logging.info("Found {} jobs to check on".format(len(jobs)))
    for job in jobs:
        cluster = cluster_registry.get_cluster(job.cluster_name)
        status = cluster.get_status(job)
        logging.info("Before: ", status, job.id)
        status = cluster.get_status(job)
        logging.info("After: ", status, job.id)
        job.status = status
        # if confout.gro exists, then the job is considered to be stopped
        if os.path.exists("{}/confout.gro".format(job.local_workdir)):
            job.status = Status.Stopped
        # if jobs is cancelled, then resubmit
        if job.status == Status.Cancelled:
            cluster.submit(job)
        session.add(job)
        session.commit()


def process_fetch(session: Session, args: argparse.Namespace, /) -> None:
    logging.info("Fetching")
    jobs = [
        job
        for job in session.query(Job).order_by(Job.id)
        if job.status != Status.Stopped
    ]
    for job in jobs:
        cluster = cluster_registry.get_cluster(job.cluster_name)
        cluster.pull(job)


def main():
    args = parse_args()

    # Lock the file
    with open("/tmp/qserver.lock", "w+") as x:
        fcntl.flock(x, fcntl.LOCK_EX | fcntl.LOCK_NB)

        config = create_configuration()
        engine = create_engine(config.engine_file)
        Session = sessionmaker(bind=engine)
        with Session() as session:
            if args.action == "resubmit":
                process_resubmit(session, args)
            if args.action == "fetch":
                process_fetch(session, args)

        # Release the lock
        fcntl.flock(x, fcntl.LOCK_UN)


if __name__ == "__main__":
    main()
