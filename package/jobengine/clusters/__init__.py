
from . import arcus
from . import arcusb
from . import biowulf
from . import biowulf2
from . import archer

clusters = {
    "biowulf": biowulf.Biowulf,
    "biowulf2": biowulf2.Biowulf2,
    "arcus-b": arcusb.ArcusB,
    "arcus": arcus.Arcus,
    "archer": archer.Archer,
    }

class Clusters(object):


    def __init__(self):
        self._cache = {}

    def get_cluster(self, cluster_name, caching=True):
        """Given a cluster name, returns a Cluster object and a connected shell

        :Returns: tuple, with Cluster object and an open, connected shell

        """
        cluster_name = cluster_name.lower()
        # check if we have the cluster in the cache already
        if caching and self._cache.has_key(cluster_name):
            return self._cache[cluster_name]
        # check if we have the cluster at all
        if not cluster_name in clusters:
            return None, None
        cluster = clusters[cluster_name]

        cluster = cluster()
        shell = cluster.connect()
        self._cache[cluster_name] = (cluster, shell)\

        return cluster, shell
