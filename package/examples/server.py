import time
# sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine 
# jobengire
from jobengine.core import Job
from jobengine.clusters import Jade
from jobengine.configuration import engine_file

engine = create_engine(engine_file)
Session = sessionmaker(bind=engine)
session = Session()

cluster = Jade()
shell = cluster.connect()
    
while True:
    print("Checking")
    jobs = [job for job in session.query(Job).order_by(Job.id)]
    for job in jobs :
        print job
        continue
        status = cluster.get_status(shell, job)
        job.status = status 
        print(status, job.id)
        if status == "C":
            job = cluster.submit(shell, job)
            print(job.status, job.id)
        session.add(job)
        session.commit()
        cluster.pull(shell, job)   
        print(job.status, job.id, job.workdir)
    #break
    time.sleep(5)
    
