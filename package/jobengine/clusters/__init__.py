
from jade import Jade
from emerald import Emerald
from arcus import Arcus
from hal import Hal
from skynet import Skynet
from biowulf import Biowulf

__all__ = ["Jade", "Biowulf", "Emerald", "Arcus", "Skynet", "Hal", "Clusters"]

class Clusters(object):
    clusters = {"jade": Jade, "emerald": Emerald, "arcus": Arcus, "hal": Hal, "skynet": Skynet, "biowulf": Biowulf}
    def __init__(self):
        self.__clusters_cache = {}    
    def get_cluster(self, cluster_name):
        cluster_name = cluster_name.lower()
        if self.__clusters_cache.has_key(cluster_name):
            return self.__clusters_cache[cluster_name]
        cluster = self.clusters[cluster_name]
        
        cluster = cluster()
        shell = cluster.connect()
        self.__clusters_cache[cluster_name] = (cluster, shell)
        return cluster, shell
      
