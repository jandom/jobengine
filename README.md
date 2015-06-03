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

Save time, avoid manual labour. 

Advantages
----------

* use different clusters
    learn once, and manage your jobs accross multiple computing clusters
* automatically download results
    use a cron job to fetch data from clusturs
* modify your directory structure
    no more worries about moving/renaming directories on your local machine
* distributed computing
    works with any submission system
* easy backup
    research data is stored in one centralized location, ~/.lockers

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



