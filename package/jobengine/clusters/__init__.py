
from jade import Jade
from emerald import Emerald
from arcus import Arcus
from hal import Hal
from skynet import Skynet
from biowulf import Biowulf, BiowulfMartini
from biowulf2 import Biowulf2
from biowulf2ib import Biowulf2IB

__all__ = ["Jade", "Biowulf", "Biowulf2", "Biowulf2IB","BiowulfMartini", "Emerald", "Arcus", "Skynet", "Hal", "Clusters"]

class Clusters(object):
    
    clusters = {"jade": Jade, "arcus": Arcus, "biowulf": Biowulf, "biowulf-martini": BiowulfMartini, "biowulf2": Biowulf2, "biowulf2ib": Biowulf2IB, "arcus-gpu": Arcus, "emerald": Emerald}
    def __init__(self):
        self.__clusters_cache = {}    
    def get_cluster(self, cluster_name, caching=False):
        cluster_name = cluster_name.lower()
        # check if we have the cluster in the cache already
        if caching and self.__clusters_cache.has_key(cluster_name):
            return self.__clusters_cache[cluster_name]
        # check if we have the cluster at all
        if not cluster_name in self.clusters:
            return None, None
        cluster = self.clusters[cluster_name]
        
        cluster = cluster()
        shell = cluster.connect()
        self.__clusters_cache[cluster_name] = (cluster, shell)
        return cluster, shell
      
