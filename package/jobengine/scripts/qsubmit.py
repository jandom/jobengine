#!/usr/bin/env python

from jobengine.clusters import Clusters
from jobengine.core import Job, create  , get_job_from_workdir
from jobengine.configuration import engine_file

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

import argparse, os

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topol", default="topol.tpr")
    parser.add_argument("--jobname", default="workdir")
    parser.add_argument("--cluster", default="arcus-gpu")
    parser.add_argument("--workdir", "-w", default=None)
    parser.add_argument("--duration", default="24:00:00")
    parser.add_argument("--nodes", type=int, default=1)
    parser.add_argument("--processes", type=int, default=16)
    parser.add_argument("--script", default=None)
    return parser.parse_args()

def main():
    args = parse_args()
    
    engine = create_engine(engine_file)
    Job.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()

    if not args.workdir and os.path.exists("workdir"): args.workdir = "workdir"
    
    # Restore an existing workdir
    if args.workdir:
        job = get_job_from_workdir(session, args.workdir)
        print job
        if job.status == "Q" or job.status == "R" or job.status == "PD": 
            print("Job already running or queued")
            return        
        cluster, shell = Clusters().get_cluster(job.cluster_name)
        job = cluster.submit(shell, job, duration=args.duration)
        status = cluster.get_status(shell, job)
        job.status = status
        session.add(job)
        session.commit()       
    # Create a brand-new workdir    
    else:
        cluster, shell = Clusters().get_cluster(args.cluster)
        job = create(args.topol, cluster, shell, args.jobname, args.duration, args.nodes, args.processes, args.script)
        assert(job)
        print job
        status = cluster.get_status(shell, job)
        print status
        if not job.cluster_id:
            job = cluster.submit(shell, job)
        print status            
        session.add(job)
        session.commit()

if __name__ == "__main__":
    main()                 
