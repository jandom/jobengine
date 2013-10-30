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
    parser.add_argument("--workdir", default="workdir")
    return parser.parse_args()

def main():
    args = parse_args()
    
    engine = create_engine(engine_file)
    Session = sessionmaker(bind=engine)
    session = Session()
    clusters = Clusters()    
    
    job = get_job_from_workdir(session, args.workdir)
    
    if job.status == "S": return
    cluster, shell = clusters.get_cluster(job.cluster_name)
    print job, cluster, shell
    cluster.delete(shell, job.cluster_id)
    job.status = "S" # Stopped
    session.add(job)
    session.commit()
    #for j in jobs: print j.uuid
if __name__ == "__main__":
    main()