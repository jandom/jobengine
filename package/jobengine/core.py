

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

     def __init__(self, name, uuid, workdir, local_workdir, remote_workdir, cluster_name, cluster_id, nodes=1):
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

def copy_glob_to_local_locker(pattern, workdir):
	  for f in glob.glob(pattern):
		    if os.path.exists(f):
			      shutil.copy(f, workdir)

def create(tpr, cluster, shell, job_name="workdir", duration="24:00:00", nodes=1, processes=16, script=None):
    """

      - Argument validation
      - Copy from cwd to locker (on local machine)
      - Copy from local locker to remote locker
      - Submit 

    """
    assert os.path.isfile(tpr)
    assert os.path.splitext(tpr)[1] == ".tpr"
    if not os.path.exists(configuration.config.lockers): os.mkdir(configuration.config.lockers)
    
    # Create workdir, copy files over there
    assert not os.path.exists("workdir")
    id0 = str(uuid.uuid4())
    workdir = "%s/%s" % (configuration.config.lockers, id0)
    os.mkdir(workdir)
    os.symlink(workdir, "workdir")
    local_dir = os.path.dirname(tpr) # FIXME this should be stored
    shutil.copy(tpr, workdir)
    
    copy_glob_to_local_locker("topol*.tpr", workdir)
    copy_glob_to_local_locker("plumed.dat*", workdir)
    copy_glob_to_local_locker("HILLS*", workdir)
    copy_glob_to_local_locker("*.mdp", workdir)
    copy_glob_to_local_locker("*.pdb", workdir)
    copy_glob_to_local_locker("*.gro", workdir)

    import distutils.core
    
    # Rob's umbrella sampling code
    def copy_to_local_locker(local_dir, dirname):
        dir = os.path.join(local_dir, dirname)
        if os.path.exists(dir):
            os.mkdir("{}/{}".format(workdir, dirname)) 
            distutils.dir_util.copy_tree(dir, "{}/{}".format(workdir, dirname))
    
    
    copy_to_local_locker(local_dir, "tpr")
    copy_to_local_locker(local_dir, "tprs")
    copy_to_local_locker(local_dir, "qij")
    copy_to_local_locker(local_dir, "qvt")
    copy_to_local_locker(local_dir, "mdp")
    
    print("nodes=", nodes, "processes=",processes, "id=", id0)
    
    # Setup SSH client to copy files over via scp
    scp = SCPClient(shell.get_transport(), socket_timeout = 600)

    try:
        scp.put(workdir, "%s/.lockers/" % (cluster.path), recursive=True)
    except SCPException, e:
        print "SCPException",e
        shutil.rmtree(workdir)
        os.remove("workdir")
        return None
    
    remote_workdir = "%s/.lockers/%s" % (cluster.path, id0)
    print remote_workdir
    cluster_id = 0 
    job = Job(job_name, id0, workdir, local_dir, remote_workdir, cluster.name, cluster_id, nodes)

    
    job = cluster.submit(shell, job, nodes=nodes, duration=duration)
    return job
        
