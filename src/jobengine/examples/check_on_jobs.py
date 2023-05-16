import logging
import time

from sqlalchemy import create_engine

# sqlalchemy
from sqlalchemy.orm import sessionmaker

from jobengine.clusters.concrete_clusters import biowulf2
from jobengine.configuration import create_configuration
from jobengine.model.job import Job
from jobengine.status import Status


def main():
    config = create_configuration()
    engine = create_engine(config.engine_file)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        cluster = biowulf2.Biowulf2()

        while True:
            logging.info("Checking...")
            for job in session.query(Job).order_by(Job.id):
                logging.info(f"Found {job=}")
                status = cluster.get_status(job)
                job.status = status
                logging.info(f"{status=} {job.id=}")
                if status == Status.Cancelled:
                    job = cluster.submit(job)
                    logging.info(job.status, job.id)
                session.add(job)
                session.commit()
                cluster.pull(job)
                logging.info((job.status, job.id, job.workdir))
            time.sleep(5)


if __name__ == "__main__":
    main()
