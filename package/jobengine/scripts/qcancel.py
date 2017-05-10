#!/usr/bin/env python

from jobengine.clusters import Clusters
from jobengine.core import Job, create  , get_job_from_workdir
from jobengine.configuration import engine_file
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from jobengine.configuration import engine_file
import argparse, os

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", "-w", default=["workdir"], nargs="+")
    parser.add_argument("--dry", "-d", action='store_true', help="Mark as cancelled in the database, but don't actually kill the job on the cluster")
    return parser.parse_args()

def main():
    args = parse_args()

    engine = create_engine(engine_file)
    Session = sessionmaker(bind=engine)
    session = Session()
    clusters = Clusters()

    for workdir in args.workdir:
	print(workdir)
    	job = get_job_from_workdir(session, workdir)
        if not job: continue
        if not args.dry:
            cluster, shell = clusters.get_cluster(job.cluster_name)
            print(cluster, shell)
            cluster.cancel(shell, job)
    	job.status = "S" # Stopped
    	session.add(job)
        session.commit()

if __name__ == "__main__":
    main()
