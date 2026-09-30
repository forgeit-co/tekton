from threading import Lock

from sqlalchemy import inspect
from sqlalchemy.exc import NoInspectionAvailable

from tekton.infrastructure.orm import tables
from tekton.infrastructure.orm.meta_record import MetaRecord
from tekton.infrastructure.orm.orm import mapper_registry

_registry_lock = Lock()


def run_all_mappers() -> None:
    with _registry_lock:
        try:
            inspect(MetaRecord)
        except NoInspectionAvailable:
            mapper_registry.map_imperatively(MetaRecord, tables.meta)
