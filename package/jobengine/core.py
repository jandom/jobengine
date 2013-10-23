from jobengine.clusters import Emerald, Jade


import configuration
import spur
import uuid
import os
import shutil
#shell = spur.SshShell(hostname="localhost", username="bob", password="password1")

from paramiko import SSHClient
from scp import SCPClient

# SQAlchemy-related
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
Base = declarative_base()

class Job(Base):
     __tablename__ = 'jobs'

     id = Column(Integer, primary_key=True)
     name = Column(String)
     uuid = Column(String)
     workdir = Column(String)
     remote_workdir = Column(String)
     cluster_name = Column(String)
     cluster_id = Column(Integer)
     
     status = Column(String)

     def __init__(self, name, uuid, workdir, remote_workdir, cluster_name, cluster_id):
         self.name = name
         self.uuid = uuid
         self.workdir = workdir
         self.remote_workdir = remote_workdir
         self.cluster_name = cluster_name
         self.cluster_id = cluster_id
         self.status = "U"
         

     def __repr__(self):
        return "<Job Id:%d UUID:%s\nWorkdir:%s\nRemote workdir:%s\n'%s'>" % (self.id if self.id else 0, self.uuid, self.workdir, self.remote_workdir, self.name)

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

def submit(tpr, cluster):
    assert os.path.isfile(tpr)
    if not os.path.exists(configuration.lockers): os.mkdir(configuration.lockers)
    assert not os.path.exists("workdir")
    id0 = str(uuid.uuid4())
    workdir = "%s/%s" % (configuration.lockers, id0)
    os.mkdir(workdir)
    os.symlink(workdir, "workdir")
    shutil.copy(tpr, workdir)
    open("%s/submit.sh" % workdir,"w").write(cluster.script)
    
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

def create(tpr, cluster, job_name="workdir"):
    assert os.path.isfile(tpr)
    if not os.path.exists(configuration.lockers): os.mkdir(configuration.lockers)
    assert not os.path.exists("workdir")
    id0 = str(uuid.uuid4())
    workdir = "%s/%s" % (configuration.lockers, id0)
    os.mkdir(workdir)
    os.symlink(workdir, "workdir")
    shutil.copy(tpr, workdir)
    open("%s/submit.sh" % workdir,"w").write(cluster.script % job_name)
    
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(cluster.hostname, username=cluster.username)
    scp = SCPClient(ssh.get_transport())
    scp.put(workdir, "%s/.lockers/" % (cluster.path), recursive=True)
    
    shell = cluster.connect()
    
    with shell:
        remote_workdir = "%s/.lockers/%s" % (cluster.path, id0)
        #result = shell.run(["qsub","%s/.lockers/%s/submit.sh" % (cluster.path, id0)], cwd=remote_workdir)
        #cluster_id = cluster.parse_qsub(result)
        j = Job(job_name, id0, workdir, remote_workdir, cluster.name, None)
    return j        
        