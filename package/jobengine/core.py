

import spur
import uuid
import os, glob
import shutil

from paramiko import SSHClient
from scp import SCPClient, SCPException

# SQAlchemy-related
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from . import configuration
Base = declarative_base()

class Job(Base):
     __tablename__ = 'jobs'

     id = Column(Integer, primary_key=True)
     name = Column(String)
     uuid = Column(String)
     workdir = Column(String)
     remote_workdir = Column(String)
     local_workdir = Column(String)
     #local_dir = Column(String)
     cluster_name = Column(String)
     cluster_id = Column(Integer)
     nodes = Column(Integer)
     status = Column(String)
     partition = Column(String)

     def __init__(self, name, uuid, workdir, local_workdir, remote_workdir, cluster_name, cluster_id, nodes=1, partition=None):
         self.name = name
         self.uuid = uuid
         self.workdir = workdir
         self.remote_workdir = remote_workdir
         self.cluster_name = cluster_name
         self.cluster_id = cluster_id
         self.status = "U"
         self.local_workdir = local_workdir
         self.current_chemtime = 0.0
         self.target_chemtime = 0.01
         self.nodes = nodes
         self.partition = partition
         

     def __repr__(self):
        return "<Job '%s Cluster: %s'>\n\tId: %d Cluster Id: %d Status: %s UUID: %s\n\tWorkdir: %s\n\tRemote workdir: %s" % (self.name, self.cluster_name, 
                                                                                                                  self.id if self.id else 0,
                                                                                                                  self.cluster_id if self.cluster_id else 0 ,
                                                                                                                  self.status,
                                                                                                                  self.uuid, self.workdir, self.remote_workdir,)

def get_job_from_workdir(session, workdir):
    uuid0 = os.path.basename(os.path.realpath(workdir))
    jobs = [job for job in session.query(Job).order_by(Job.id) if job.uuid == uuid0]
    assert(len(jobs) == 1)
    job = jobs[0]    
    return job

def create(tpr, cluster, shell, job_name="workdir", duration="24:00:00", nodes=1, processes=16, script=None, partition=None, ntasks_per_node=16):
    """

      - Argument validation
      - Copy from cwd to locker (on local machine)
      - Copy from local locker to remote locker
      - Submit 

    """
    if not os.path.exists(configuration.config.lockers): os.mkdir(configuration.config.lockers)
    
    # Create workdir, copy files over there
    assert not os.path.exists("workdir")
    id0 = str(uuid.uuid4())
    workdir = "%s/%s" % (configuration.config.lockers, id0)
    
    local_dir = os.getcwd()
    ignore = shutil.ignore_patterns("\#*", "workdir*", "analysis*", "test*", "*topol*.top")
    print("local copy:", "src=", local_dir, "dst=", workdir)
    shutil.copytree(local_dir, workdir, symlinks=False, ignore=ignore)
    os.symlink(workdir, "workdir")

    # Setup SSH client to copy files over via scp
    dst = "%s/.lockers/" % (cluster.path)
    print("remote copy:", "src=", workdir, "dst=", cluster.name,":",)
    scp = SCPClient(shell.get_transport(), socket_timeout = 600)
    try:
        scp.put(workdir, dst, recursive=True)
    except SCPException, e:
        print "SCPException",e
        shutil.rmtree(workdir)
        os.remove("workdir")
        return None
    
    remote_workdir = "%s/.lockers/%s" % (cluster.path, id0)
    
    #if not partition: cluster.partitions[0]

    print("nodes=", nodes, "processes=",processes, "id=", id0, "partition=", partition)

    cluster_id = 0 
    job = Job(job_name, id0, workdir, local_dir, remote_workdir, cluster.name, cluster_id, nodes, partition)

    
    job = cluster.submit(shell, job, nodes=nodes, duration=duration, partition=partition, ntasks_per_node=ntasks_per_node)
    return job
        
