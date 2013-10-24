#!/usr/bin/env python

from jobengine.clusters import Clusters
from jobengine.core import Job, create  
from jobengine.configuration import engine_file

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topol", default="topol.tpr")
    parser.add_argument("--jobname", default="workdir")
    parser.add_argument("--cluster", default="jade")
    return parser.parse_args()

def main():
    args = parse_args()
    
    #emerald = Emerald()
    #shell = emerald.connect()
    
    cluster, shell = Clusters().get_cluster(args.cluster)
    
    engine = create_engine(engine_file)
    Job.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    if True:
        
        #result = shell.run(["echo", "-n", "hello"])
        
        #job = submit("topol.tpr", jade)
        job = create(args.topol, cluster, args.jobname)
        print job
        status = cluster.get_status(shell, job)
        print status
        job = cluster.submit(shell, job)
        print status    
        
        session.add(job)
        session.commit()

if __name__ == "__main__":
    main()                 
