

from jobengine.clusters import Clusters
import hashlib
import numpy as np

def md5sum(f):
  
    return hashlib.md5(open(f).read()).hexdigest()

def test_rsync():
    
    f = "data/M2__monomer__charmm36__charmm22stprot__tip3p__strand_bilayer__run_1.tpr"
    
    clusters = Clusters()
    names = clusters.clusters.keys()
    names = ["jade", "arcus", "biowulf"]
    for name in names:
        cluster, shell = clusters.get_cluster(name)
        print cluster    
        output = "{}.tpr".format(name)
        cluster.test_push(shell, f, "/tmp/topol.tpr", verbose=False)
        cluster.test_pull(shell, "/tmp/topol.tpr", output, verbose=False)
        desired = md5sum(f)
        actual = md5sum(output)
        print desired, actual
        np.testing.assert_equal(actual, desired)
    print("Testing complete, closing down")

if __name__ == "__main__":
    test_rsync()