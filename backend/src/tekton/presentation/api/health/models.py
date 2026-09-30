from pydantic import BaseModel, ConfigDict


class WireModel(BaseModel):
    model_config = ConfigDict(json_schema_serialization_defaults_required=True)


class HealthOut(WireModel):
    status: str
    schema_revision: str
