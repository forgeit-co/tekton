from tekton.infrastructure.orm import tables
from tekton.infrastructure.orm.meta_record import MetaRecord
from tekton.infrastructure.orm.orm import mapper_registry


def run_all_mappers() -> None:
    mapper_registry.map_imperatively(MetaRecord, tables.meta)
