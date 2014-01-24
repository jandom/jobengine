#!/usr/bin/env python

from jobengine.clusters import Clusters
from jobengine.core import Job, create  , get_job_from_workdir
from jobengine.configuration import engine_file

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topol", default="topol.tpr")
    parser.add_argument("--jobname", default="workdir")
    parser.add_argument("--cluster", default="jade")
    parser.add_argument("--workdir", default=None)
    parser.add_argument("--duration", default="24:00:00")
    return parser.parse_args()

def main():
    args = parse_args()
    
    engine = create_engine(engine_file)
    Job.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Restore an existing workdir
    if args.workdir:
        job = get_job_from_workdir(session, args.workdir)
        if job.status != "S": return
        cluster, shell = Clusters().get_cluster(job.cluster_name)
        print job
        job = cluster.submit(shell, job)
        print job.status
        status = cluster.get_status(shell, job)
        print job.status 
        session.add(job)
        session.commit()       
    # Create a brand-new workdir    
    else:
        cluster, shell = Clusters().get_cluster(args.cluster)
        job = create(args.topol, cluster, args.jobname, args.duration)
        assert(job)
        print job
        status = cluster.get_status(shell, job)
        print status
        job = cluster.submit(shell, job)
        print status            
        session.add(job)
        session.commit()

if __name__ == "__main__":
    main()                 
