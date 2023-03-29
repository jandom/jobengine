import time

from sqlalchemy import create_engine

# sqlalchemy
from sqlalchemy.orm import sessionmaker

from jobengine.clusters.concrete_clusters import biowulf2
from jobengine.configuration import create_configuration

# jobengire
from jobengine.job import Job


def main():
    config = create_configuration()
    engine = create_engine(config.engine_file)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        cluster = biowulf2.Biowulf2()
        shell = cluster.connect()

        while True:
            print("Checking...")
            for job in session.query(Job).order_by(Job.id):
                print(job)
                status = cluster.get_status(job)
                job.status = status
                print((status, job.id))
                if status == "C":
                    job = cluster.submit(shell, job)
                    print((job.status, job.id))
                session.add(job)
                session.commit()
                cluster.pull(shell, job)
                print((job.status, job.id, job.workdir))
            # break
            time.sleep(5)


if __name__ == "__main__":
    main()
