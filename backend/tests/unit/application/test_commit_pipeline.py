from sqlalchemy import text
from sqlalchemy.engine import Engine

from tekton.application.commit.pipeline import CommitPipeline
from tekton.infrastructure.shared.unit_of_work import SqlAlchemyUnitOfWork


def test_commit_pipeline_persists_after_collecting_events(
    commit_pipeline: CommitPipeline,
    unit_of_work_with_pending_write: SqlAlchemyUnitOfWork,
    engine_with_commit_table: Engine,
):
    with unit_of_work_with_pending_write as unit_of_work:
        unit_of_work.execute(text("INSERT INTO committed_values (value) VALUES ('saved')"))
        commit_pipeline.commit(unit_of_work, unit_of_work)

    with engine_with_commit_table.connect() as connection:
        persisted_values = connection.execute(text("SELECT value FROM committed_values")).all()

    assert persisted_values == [("saved",)], "Commit pipeline must persist the collected write"
