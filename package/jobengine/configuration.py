import paramiko
from os.path import expanduser
import os

class Struct:
  '''The recursive class for building and representing objects with.'''
  def __init__(self, obj):
    for k, v in obj.iteritems():
      if isinstance(v, dict):
        setattr(self, k, Struct(v))
      else:
        setattr(self, k, v)
  def __getitem__(self, val):
    return self.__dict__[val]
  def __repr__(self):
    return '{%s}' % str(', '.join('%s : %s' % (k, repr(v)) for
      (k, v) in self.__dict__.iteritems()))


private_key_file=os.path.join(os.environ["HOME"], ".ssh", "id_dsa")
lockers = os.path.join(os.environ["HOME"],".lockers")
engine_file = 'sqlite:///%s/jobengine.sql' % lockers	  		

if not os.path.exists(private_key_file):
	raise IOError("Private key file doesn't exist at '{}'".format(private_key_file))
dsa_key = paramiko.DSSKey.from_private_key_file(private_key_file)

ssh_config_file = '{}/.ssh/config'.format(expanduser("~"))
if not os.path.exists(ssh_config_file):
	raise IOError("SSH config file doesn't exist at '{}'".format(ssh_config_file))
ssh = paramiko.SSHConfig()
ssh.parse(open(ssh_config_file))

config = {
	"engine_file": engine_file,
	"private_key_file": private_key_file,
	"lockers": lockers,
	"rsync": {
		"flags": "-a --compress",
	},
	"ssh": ssh,
	"dsa_key": dsa_key,

}


config = Struct(config)