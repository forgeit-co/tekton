from sqlalchemy import Column, String, Table

from tekton.infrastructure.orm.orm import metadata

meta = Table(
    "meta",
    metadata,
    Column("key", String, primary_key=True),
    Column("value", String, nullable=False),
)
