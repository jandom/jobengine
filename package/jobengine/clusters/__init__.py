
from jade import Jade
from emerald import Emerald
from arcus import Arcus
from hal import Hal
from skynet import Skynet
from biowulf import Biowulf, BiowulfMartini

__all__ = ["Jade", "Biowulf","BiowulfMartini", "Emerald", "Arcus", "Skynet", "Hal", "Clusters"]

class Clusters(object):
    clusters = {"jade": Jade, "emerald": Emerald, "arcus": Arcus, "hal": Hal, "skynet": Skynet, "biowulf": Biowulf}
    clusters = {"jade": Jade, "arcus": Arcus, "biowulf": Biowulf, "biowulf-martini": BiowulfMartini, "arcus-gpu": Arcus, "chronos": Chronos}
    def __init__(self):
        self.__clusters_cache = {}    
    def get_cluster(self, cluster_name, caching=False):
        cluster_name = cluster_name.lower()
        if caching and self.__clusters_cache.has_key(cluster_name):
            return self.__clusters_cache[cluster_name]
        cluster = self.clusters[cluster_name]
        
        cluster = cluster()
        shell = cluster.connect()
        self.__clusters_cache[cluster_name] = (cluster, shell)
        return cluster, shell
      
