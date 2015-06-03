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

def main():
    args = parse_args()
  
    engine = create_engine(engine_file)
    Session = sessionmaker(bind=engine)
    session = Session()
    clusters = Clusters()
    
    job = get_job_from_workdir(session, args.workdir)
    print job
    
    cluster, shell = clusters.get_cluster(job.cluster_name)
    print cluster, shell

    return_code = cluster.delete(shell, job)   
    assert(return_code==0)

if __name__ == '__main__':
    main()    
