import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jobengine.clusters.cluster_registry import biowulf2
from jobengine.configuration import create_configuration
from jobengine.controller import create


def main():
    cluster = biowulf2.Biowulf2()
    stdout, _ = cluster.run_shell_command(["echo", "-n", "hello"])

    logging.info(stdout)

    config = create_configuration()
    engine = create_engine(config.engine_file)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        job = create.create("topol.tpr", cluster)
        logging.info(job)

        status = cluster.get_status(job)
        logging.info(status)

        cluster.submit(job)
        logging.info(job.status)

        session.add(job)
        session.commit()


if __name__ == "__main__":
    main()
