from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ErrorInfo(BaseSchema):
    code: str
    message: str
    trace_id: str | None = None


class ErrorResponse(BaseSchema):
    error: ErrorInfo
