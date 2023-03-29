import os

from sqlalchemy.orm import Session

from jobengine.job import Job


def get_job_from_workdir(*, session: Session, workdir: str) -> Job:
    uuid0 = os.path.basename(os.path.realpath(workdir))
    # FIXME this gets all the Job objects from the database (bad)
    jobs = [job for job in session.query(Job).order_by(Job.id) if job.uuid == uuid0]
    [job] = jobs
    return job
