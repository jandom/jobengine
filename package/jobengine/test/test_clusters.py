

import jobengine.clusters
clusters = jobengine.clusters.Clusters()
for k, v in clusters.clusters.items():
    print k, v
    if k != "biowulf": continue
    cluster, shell = clusters.get_cluster(k)
    if not hasattr(cluster, "get_status_all"): continue
    print cluster.get_status_all(shell)