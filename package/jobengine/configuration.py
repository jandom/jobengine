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

config = {
	"engine_file": engine_file,
	"private_key_file": None,
	"lockers": lockers,
	"rsync": {
		"flags": "-a --compress",
	},
	"ssh": None,
	"dsa_key": None,

}


config = Struct(config)
