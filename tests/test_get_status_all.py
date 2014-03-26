

import jobengine.clusters
clusters = jobengine.clusters.Clusters()
names = ["jade", "biowulf", "arcus",]
for name in names:
    print name
    cluster, shell = clusters.get_cluster(name)
    print cluster
    if not hasattr(cluster, "get_status_all"): continue
    print cluster.get_status_all(shell)
    
print("Testing complete, closing down")