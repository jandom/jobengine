from sqlalchemy import create_engine, inspect

from jobengine import configuration
from jobengine.model.job import Job


def test_create_configuration(tmp_path):
    config = configuration.create_configuration(tmp_path)

    assert (tmp_path / ".lockers").exists()
    assert (tmp_path / ".lockers" / "jobengine.sql").exists()

    engine = create_engine(config.engine_file)
    inspector = inspect(engine)
    inspector.reflect_table(Job.__table__, None)

    # Get the sets of columns in the model and in the database
    expected_columns = {column.name for column in Job.__table__.c}
    actual_columns = {
        column["name"] for column in inspector.get_columns(Job.__tablename__)
    }
    assert expected_columns == actual_columns
