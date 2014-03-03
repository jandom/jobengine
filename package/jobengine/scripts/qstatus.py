#!/usr/bin/env python

from jobengine.clusters import Clusters
from jobengine.core import Job, create  , get_job_from_workdir
from jobengine.configuration import engine_file

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker




import cherrypy
class HelloWorld(object):
    def index(self):

        clusters = Clusters()
        
        output = []
        
        for k, v in clusters.clusters.items():
            print k
            if k == "skynet": continue
            #if k == "biowulf": continue
            cluster, shell = clusters.get_cluster(k)
            output.append("==={0}===\n".format(k))
            output.append(cluster.get_status_all(shell))
            
        return "<pre>{0}</pre>".format("".join(output))
    index.exposed = True

cherrypy.quickstart(HelloWorld())
