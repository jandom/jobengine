#!/usr/bin/env python

import commands
from xml.dom import minidom
#xmldoc = minidom.parse('qstat.xml')
xmldoc = minidom.parseString(commands.getoutput("qstat -x"))
joblist = xmldoc.getElementsByTagName('Job') 

for job in joblist:
    jobname = job.getElementsByTagName('Job_Name')[0].lastChild.data
    jid = job.getElementsByTagName('Job_Id')[0].lastChild.data
    jid = jid.split(".")[0]
    t1 = "00:00:00"
    if job.getElementsByTagName('resources_used'):
    	t1 = job.getElementsByTagName('resources_used')[0].getElementsByTagName('cput')[0].lastChild.data
    t2 = job.getElementsByTagName('Resource_List')[0].getElementsByTagName('walltime')[0].lastChild.data
    pwd = job.getElementsByTagName('init_work_dir')[0].lastChild.data
    print ("%-70s" % jobname), jid, t1, t2, pwd
