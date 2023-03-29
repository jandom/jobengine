from jobengine.clusters.abstract_clusters.base_cluster import BaseCluster


class Localhost(BaseCluster):
    name = "localhost"
    hostname = "127.0.0.1"
    path = "/tmp/"
