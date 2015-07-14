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

Example ssh config file
=======================

```
# Place inside ~/.ssh/config

Host biowulf2
   HostName biowulf2.nih.gov
   User domanskij
   #LogLevel QUIET
   #IdentityFile ~/.ssh/id_dsa
   #ProxyCommand ssh domanski@clathrin.bioch.ox.ac.uk exec nc %h %p




