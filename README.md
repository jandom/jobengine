jobengine
=========

Manage MD simulations across multiple computing clusters


Origins
-------

jobengine was a tool used in a company I used to work for. D. E. Shaw Research
built this awesome, special-purpose super-computer that was generating tons of numerical
simulation data. jobengine, their jobengine, was a tool for sending computational
jobs to that super-computer and managing the simulation data and metadata. 

This jobengine that I'm making available here is a testament to the ingenuity of 
the engineers who built the original jobengine.  

Aim
---

Saving time. Researchers loooovveee to upload and download their jobs to clusters. 
This sucks and is tedious.

Advantages
----------

* send simulations to different clusters, seemlessly, from your workstation
* avoid rsyncing your simulation data from clusters by hand (done in background automatically)
* re-arrange your directory structure without breaking the place where data is stored
* store mete-data about your simulations (current chemical time, target chemical time)
* makes backing up really, really easy (single location to syncronize)

Limitations
----------- 

* only supports gromacs

Examples
--------

Submit a job, given a tpr

    `qsubmit.py --cluster biowulf --topol topol.tpr` or 
    `qsubmit.py --cluster oxford-cluster-1 --topol topol.tpr`

Fetch some results, manually

    `qfetch.py`
    
Cancel a job, then re-submit manually

    `qcancel.py`    
    `qsubmit.py --workdir workdir`
    
Add to crontabe to re-submit broken jobs (every 30 mins) and fetch results (every 60 mins),     

    `*/30 * * * * qserver.py`
    `*/60 * * * * qserver.py --action fetch`    



