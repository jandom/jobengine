from jobengine.clusters.concrete_clusters import biowulf


def test_parse_biowulf_cluster_id():
    cluster_id = biowulf.parse_biowulf_cluster_id(["1234.biobos"])
    assert cluster_id == 1234
