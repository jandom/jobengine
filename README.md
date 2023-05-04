jobengine
=========

Manage MD simulations across multiple computing clusters

Installation
------------

    pip install git+https://github.com/jandom/jobengine.git

Sanity check
------------

    $ python -c "import jobengine; print(jobengine)"
    <module 'jobengine' from '/private/tmp/test/venv/lib/python3.9/site-packages/jobengine/__init__.py'>

Examples
--------

Submit a job to a remote cluster, given a .tpr file in your current working directory

    qsubmit.py --cluster my_cluster --topol topol.tpr --nodes 16
    qsubmit.py --cluster my_cluster

Fetch some results from a remote cluster, manually

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

Add to cron tab to re-submit broken jobs (every 30 mins) and fetch results (every 60 mins),

Edit crontable using

    crontab -e

And add

    @hourly python ~/.local/bin/qserver.py --action fetch --cluster biowulf2
    @hourly python ~/.local/bin/qserver.py --cluster biowulf2
    */30 * * * * qserver.py
    */60 * * * * qserver.py --action fetch

Advanced
========

Adding your own clusters
------------------------

TODO

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
