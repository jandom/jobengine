from jobengine.clusters import Jade, Emerald
from jobengine.core import Job, create  
from jobengine.configuration import engine_file

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

emerald = Emerald()
shell = emerald.connect()
jade = Jade()
shell = jade.connect()

engine = create_engine(engine_file)
Job.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

if False:
    
    #result = shell.run(["echo", "-n", "hello"])
    
    #job = submit("topol.tpr", jade)
    job = create("topol.tpr", jade)
    print job
    status = jade.get_status(shell, job)
    print status
    job = jade.submit(shell, job)
    print status    
    
    
    session.add(job)
    session.commit()
              