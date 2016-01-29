#!/usr/bin/env python
import fcntl
import time
# sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine 
# jobengire
from jobengine.core import Job
from jobengine.clusters import Clusters
from jobengine.configuration import engine_file

import argparse,  subprocess, os

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", default="resubmit")
    parser.add_argument("--cluster", default="biowulf")
    return parser.parse_args()

def process_resubmit(args):

    engine = create_engine(engine_file)
    Session = sessionmaker(bind=engine)
    session = Session()
    clusters = Clusters()
    
    if True:
        print("Checking")
        jobs = [job for job in session.query(Job).order_by(Job.id) if job.status != "S"]
        print("Found {} jobs to checkon".format(len(jobs)))
        for job in jobs :
            if job.status == "S": continue
            if args.cluster and not job.cluster_name.lower().startswith(args.cluster): continue
            print job            
            cluster, shell = clusters.get_cluster(job.cluster_name)
            if not shell: continue
            status = cluster.get_status(shell, job)
            job.status = status 
            print("Before:",status, job.id)
            if os.path.exists("{}/confout.gro".format(job.local_workdir)):
                job.status = "S"
            if job.status == "C":
                job = cluster.submit(shell, job)
                print("After:", job.status, job.id)
            session.add(job)
            session.commit()
        #break
        #time.sleep(5*60) # 5 minutes

def process_fetch(args):

    engine = create_engine(engine_file)
    Session = sessionmaker(bind=engine)
    session = Session()
    clusters = Clusters()
    
    if True:
        print("Fetching")
        jobs = [job for job in session.query(Job).order_by(Job.id)]
	print(dir(jobs[0]))
        for i, job in enumerate(jobs) :
            if job.status == "S": continue	
            if not job.cluster_name.lower().startswith(args.cluster): continue
            print(i+1, len(jobs), job)
            cluster, shell = clusters.get_cluster(job.cluster_name)
            if not shell: continue
            rsync_return_code = cluster.pull(shell, job)   

def process_test(args):
    
    engine = create_engine(engine_file)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    while True:
        print("Testing")
        jobs = [job for job in session.query(Job).order_by(Job.id)]
        for job in jobs :
            print job.local_workdir if job.local_workdir else job.name, test_workdir(job.workdir)
        break
        #time.sleep(60*60) # 60 minutes

from multiprocessing import Process    

def main():
    args = parse_args()

    x = open('/tmp/qserver.lock', 'w+')
    fcntl.flock(x, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if args.action == "resubmit":
        process_resubmit(args)
    if args.action == "fetch":
        process_fetch(args)
    if args.action == "test":
        process_test(args)

    fcntl.flock(x, fcntl.LOCK_UN)
    #Process(target=process_resubmit).start()
    #Process(target=process_fetch).start()    
    
if __name__ == '__main__':
    main()    
