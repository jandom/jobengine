import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from jobengine.clusters.cluster_registry import biowulf2
from jobengine.configuration import create_configuration
from jobengine.controller import create


def main():
    config = create_configuration()

    cluster = biowulf2.Biowulf2()
    shell = cluster.get_shell()
    result = shell.exec_command(["echo", "-n", "hello"])
    print(result)

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
