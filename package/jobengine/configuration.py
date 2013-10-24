import os

private_key_file=os.path.join(os.environ["HOME"], ".ssh", "id_dsa")

lockers = os.path.join(os.environ["HOME"],".lockers")
engine_file = 'sqlite:///%s/jobengine.sql' % lockers	  		
