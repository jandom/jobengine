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

jade = Jade()
shell = jade.connect()
    
while True:
    print("Checking")
    jobs = [job for job in session.query(Job).order_by(Job.id)]
    for job in jobs :
        status = jade.get_status(shell, job)
        job.status = status 
        print(status, job.id)
        if status == "C":
            job = jade.submit(shell, job)
            print(job.status, job.id)
        session.add(job)
        session.commit()
        jade.pull(shell, job)   
        print(job.status, job.id, job.workdir)
    #break
    time.sleep(5)
    