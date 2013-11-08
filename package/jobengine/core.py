from jobengine.clusters import Emerald, Jade


import configuration
import spur
import uuid
import os
import shutil
#shell = spur.SshShell(hostname="localhost", username="bob", password="password1")

from paramiko import SSHClient
from scp import SCPClient, SCPException

# SQAlchemy-related
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
Base = declarative_base()

class Job(Base):
     __tablename__ = 'jobs'

     id = Column(Integer, primary_key=True)
     name = Column(String)
     uuid = Column(String)
     workdir = Column(String)
     remote_workdir = Column(String)
     local_workdir = Column(String)
     cluster_name = Column(String)
     cluster_id = Column(Integer)
     
     status = Column(String)

     def __init__(self, name, uuid, workdir, local_workdir, remote_workdir, cluster_name, cluster_id,):
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
         

     def __repr__(self):
        return "<Job Id:%d UUID:%s\nWorkdir:%s\nRemote workdir:%s\n'%s Cluster: %s'>" % (self.id if self.id else 0, self.uuid, self.workdir, self.remote_workdir, self.name, self.cluster_name)

def connect(host):
    
    kwargs = {"password":host.password} if hasattr(host, "password") else {"private_key_file":configuration.private_key_file}
    
    shell = spur.SshShell(
        hostname=host.hostname,
        username=host.username,
        **kwargs
    )
    
    return shell
def stat(host, jobid=None):
    pass
    
def cancel(host):
    pass

from gromacs.fileformats import MDP
from MDAnalysis import Universe
from collections import Counter
import numpy as np
def test_workdir(workdir):
    return test_workdir_contents(os.path.join(workdir, "grompp.mdp"),
                                 os.path.join(workdir, "conf.gro"),
                                 os.path.join(workdir, "traj.xtc"),)


def test_workdir_contents(mdp_file="grompp.mdp", conf_file="conf.gro", traj_file="workdir/traj.xtc"):
    mdp = MDP(mdp_file)
   
    if not   isinstance(mdp["nsteps"],int):
        nsteps = mdp["nsteps"].split()[0]
    else:
        nsteps = mdp["nsteps"]
    target_time = int(nsteps) * mdp["dt"]  # target chemical time in ps
    if not os.path.exists(traj_file): return None, None
    u = Universe(conf_file, traj_file)
    times = [f.time for f in u.trajectory]
    
    # Check if there are no double frames
    c = Counter(times)
    c.most_common(3)
    assert(c.most_common(1)[0][1]  == 1)
    
    # Check if no frames are missing
    desired_times = list(np.arange(0.0, max(times)+mdp["dt"]*mdp["nstxtcout"], mdp["dt"]*mdp["nstxtcout"]))
    assert(len(times) == len(desired_times))
    
    return max(times), target_time

def submit(tpr, cluster):
    assert os.path.isfile(tpr)
    if not os.path.exists(configuration.lockers): os.mkdir(configuration.lockers)
    assert not os.path.exists("workdir")
    id0 = str(uuid.uuid4())
    workdir = "%s/%s" % (configuration.lockers, id0)
    os.mkdir(workdir)
    os.symlink(workdir, "workdir")
    shutil.copy(tpr, workdir)
    #open("%s/submit.sh" % workdir,"w").write(cluster.script)
    open("%s/submit.sh" % workdir,"w").write(cluster.get_script(job_name, "%s/.lockers/%s" % (cluster.path, id0))) 
    
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(cluster.hostname, username=cluster.username)
    scp = SCPClient(ssh.get_transport())
    scp.put(workdir, "%s/.lockers/" % (cluster.path), recursive=True)
    
    shell = cluster.connect()
    
    with shell:
        remote_workdir = "%s/.lockers/%s" % (cluster.path, id0)
        result = shell.run(["qsub","%s/.lockers/%s/submit.sh" % (cluster.path, id0)], cwd=remote_workdir)
        cluster_id = cluster.parse_qsub(result)
        j = Job("test", id0, workdir, remote_workdir, cluster.name, cluster_id)
    return j

def get_job_from_workdir(session, workdir):
    uuid0 = os.path.basename(os.path.realpath(workdir))
    jobs = [job for job in session.query(Job).order_by(Job.id) if job.uuid == uuid0]
    assert(len(jobs) == 1)
    job = jobs[0]    
    return job

def create(tpr, cluster, job_name="workdir"):
    assert os.path.isfile(tpr)
    assert os.path.splitext(tpr)[1] == ".tpr"
    if not os.path.exists(configuration.lockers): os.mkdir(configuration.lockers)
    assert not os.path.exists("workdir")
    id0 = str(uuid.uuid4())
    workdir = "%s/%s" % (configuration.lockers, id0)
    os.mkdir(workdir)
    os.symlink(workdir, "workdir")
    local_dir = os.path.dirname(tpr) # FIXME this should be stored
    gro = os.path.join(local_dir, "conf.gro")
    mdp = os.path.join(local_dir, "grompp.mdp")
    shutil.copy(tpr, workdir)
    shutil.copy(gro, workdir)
    shutil.copy(mdp, workdir)
    open("%s/submit.sh" % workdir,"w").write(cluster.get_script(job_name, "%s/.lockers/%s" % (cluster.path, id0)))
    
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(cluster.hostname, username=cluster.username)
    scp = SCPClient(ssh.get_transport())
    
    try:
        scp.put(workdir, "%s/.lockers/" % (cluster.path), recursive=True)
    except SCPException:
        shutil.rmtree(workdir)
        os.remove("workdir")
        return None
    shell = cluster.connect()
    
    with shell:
        remote_workdir = "%s/.lockers/%s" % (cluster.path, id0)
        #result = shell.run(["qsub","%s/.lockers/%s/submit.sh" % (cluster.path, id0)], cwd=remote_workdir)
        #cluster_id = cluster.parse_qsub(result)
        print local_dir
        j = Job(job_name, id0, workdir, local_dir, remote_workdir, cluster.name, None)
    return j        
        
