#!/usr/bin/env python

from jobengine.clusters import get_cluster
from jobengine.core import Job, create  
from jobengine.configuration import engine_file
from jobengine.clusters import Jade
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
    
    jade = Jade()
    shell = jade.connect()
    
    uuid0 = os.path.basename(os.path.realpath(args.workdir))
    
    
    jobs = [job for job in session.query(Job).order_by(Job.id) if job.uuid == uuid0]
    assert(len(jobs) == 1)
    job = jobs[0]
    if job.status == "S": return
    print job
    jade.delete(shell, job.cluster_id)
    job.status = "S" # Stopped
    session.add(job)
    session.commit()
    #for j in jobs: print j.uuid
if __name__ == "__main__":
    main()