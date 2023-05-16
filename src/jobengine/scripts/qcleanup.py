#!/usr/bin/env python

import argparse
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jobengine.configuration import create_configuration
from jobengine.model.job import Job
from jobengine.status import Status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cluster", "-c", default="biowulf")
    return parser.parse_args()


def main():
    args = parse_args()
    config = create_configuration()
    engine = create_engine(config.engine_file)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        jobs = [
            job
            for job in session.query(Job).order_by(Job.id)
            if job.cluster_name.startswith(args.cluster.upper())
        ]
        logging.info(len(jobs))
        for job in jobs:
            if job.status == Status.Stopped:
                continue
            job.status = Status.Stopped
            session.add(job)
        session.commit()


if __name__ == "__main__":
    main()
