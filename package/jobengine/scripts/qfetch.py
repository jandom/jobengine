#!/usr/bin/env python

import time
# sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine 
# jobengire
from jobengine.core import Job, test_workdir, get_job_from_workdir
from jobengine.clusters import Clusters
from jobengine.configuration import engine_file

import argparse
import subprocess

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", default="workdir")
    return parser.parse_args()

def process_fetch(args):

    engine = create_engine(engine_file)
    Session = sessionmaker(bind=engine)
    session = Session()
    clusters = Clusters()
    
    job = get_job_from_workdir(session, args.workdir)
    cluster, shell = clusters.get_cluster(job.cluster_name)

    print(job)    
    print(job.status, job.name, job.id, job.workdir)
    #if job.status == "S": return
    rsync_return_code = cluster.pull(shell, job)   
    assert(rsync_return_code==0)
    
    chemtime, target_chemtime = test_workdir(job)
    print chemtime, target_chemtime 
    # If the simulation hasn't started yet, skip
    if not (chemtime and target_chemtime): return
    # If the target chemtime hasn't been achieved, don't stop
    if not (chemtime == target_chemtime): return
    # Stop the simulation if complete
    if job.status == "S": return
    cluster.delete(shell, job.cluster_id)
    print("Stopping", job)
    job.status = "S" # Stopped
    session.add(job)
    session.commit()


def main():
    args = parse_args()
  
    process_fetch(args)

 
    
if __name__ == '__main__':
    main()    
