import spur
from base import Cluster
import paramiko
from scp import SCPClient
import jobengine.configuration
from xml.dom import minidom
from arcus import Arcus
    
class Chronos(Arcus):
    name = "arcus-chronos"
    hostname ="arcus.oerc.ox.ac.uk"
    proxy = "clathrin"
    username = "jandom"
    status_command = "/opt/gridware/torque/latest/bin/qstat -u jandom"
    status_all_command = "/opt/gridware/torque/latest/bin/qstat -u jandom"