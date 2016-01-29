jobengine
=========

Manage MD simulations across multiple computing clusters

Installation
------------

    git clone https://github.com/jandom/jobengine.git
    cd jobengine/package
    python setup.py

Test
----

    $ python -c "import jobengine; print jobengine"
    <module 'jobengine' from 'jobengine/__init__.pyc'>

Examples
--------

Submit a job, given a tpr

    qsubmit.py --cluster my_cluster --topol topol.tpr --nodes 16
    qsubmit.py --cluster my_cluster 

Fetch some results, manually

    qfetch.py
    
Cancel a job, using a default -w/-workdir or a list of workdirs

    qcancel.py 
    qcancel.py -w workdir__older
    qcancel.py --workdir workdir1 workdir2 workdir3   

Re-submit a job, using either a default -w/workdir argument. Re-submit to a different partition, using a different number of nodes

    qsubmit.py 

One can override the partition or node number used to inintialize the original job 

    qsubmit.py --partion new_partition
    qsubmit.py --nodes 32
    
Add to crontabe to re-submit broken jobs (every 30 mins) and fetch results (every 60 mins),     

Edit crontable using 

    crontab -e

And add 

    */30 * * * * qserver.py
    */60 * * * * qserver.py --action fetch    

Advanced
========

Adding your own clusters
------------------------

Create a new cluster file inside `package/jobengine/clusters/`, there is a number of clusters there from which you can start/inherit: PBSCluster, SLURMCluster. 

Create your cluster class along the existing ones and register the class in:

    package/jobengine/clusters/__init__.py

There are 3 main methods you'll have to inherit/implement:
* `doSubmit(self, shell, job,  **kwargs)` runs the submit command on the remote machine, with any flags passed in kwargs, then return stdout and stderr as tuple 
* `submit(self, shell, job, **kwargs)` calls doSubmit, parses the output/error, checks on job status and returns the updated job object
* `cancel(self, shell, job)` execute a cancel command on the remote host
There is a bunch of other methods, see base.py for a full list.


Example ssh config file
-----------------------

```
# Place inside ~/.ssh/config

Host my_cluster
   HostName my_cluster.university.edu
   User my_username_on_cluster
   # Optional arguments beloww
   # LogLevel QUIET
   # IdentityFile ~/.ssh/id_dsa
   # ProxyCommand ssh my_username_at_gateway@gateway_computer.university.edu exec nc %h %p
```

