#!/usr/bin/env python

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

from jobengine.clusters import Clusters
from jobengine.core import Job, create  , get_job_from_workdir
from jobengine.configuration import engine_file
import jobengine.configuration as configuration

from paramiko import SSHClient
from scp import SCPClient

import spur
import uuid
import argparse
import subprocess

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topol", default="topol.tpr")
    parser.add_argument("--hostname", default="129.67.76.36")
    parser.add_argument("--username", default="domanski")
    return parser.parse_args()
  
  
args = parse_args()
id0 = str(uuid.uuid4())

kwargs = {"private_key_file":configuration.private_key_file, 
          "missing_host_key":spur.ssh.MissingHostKey.accept}

shell = spur.SshShell(
    hostname=args.hostname,
    username=args.username,
    **kwargs
)
print id0
remote_dir = "/tmp/{}".format(id0)
shell.run(["mkdir", remote_dir])

cmd = "rsync  %s %s@%s:%s/ " % (args.topol, args.username, args.hostname, remote_dir)  
subprocess.call(cmd, shell=True)   
print "{} copied to {}:{}".format(args.topol, args.hostname, remote_dir)
shell.run(["mdrun", "-v"], cwd=remote_dir)

cmd = "rsync  %s@%s:%s/* . " % (args.username, args.hostname, remote_dir)  
subprocess.call(cmd, shell=True)

