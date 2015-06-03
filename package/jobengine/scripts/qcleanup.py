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
    parser.add_argument("--cluster","-c", default="biowulf")
    return parser.parse_args()

def main():
    args = parse_args()
    
    engine = create_engine(engine_file)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    
    jobs = [job for job in session.query(Job).order_by(Job.id) if job.cluster_name == args.cluster.upper()]
    
    print len(jobs )
    for job in jobs :
        if job.status == "S": continue
        job.status = "S"    
        
        session.add(job)
    session.commit()

if __name__ == "__main__":
    main()
