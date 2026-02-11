from datetime import datetime
import uuid

from pydantic import BaseModel, model_validator

from app.models.enums import MaterialType
from app.schemas.common import BaseSchema


class MaterialCreate(BaseModel):
    group_id: uuid.UUID
    title: str
    body_text: str | None = None
    type: MaterialType = MaterialType.lecture
    link_url: str | None = None
    is_published: bool = False

    @model_validator(mode="after")
    def validate_link(self):
        if self.type in {MaterialType.link, MaterialType.file} and not self.link_url:
            raise ValueError("link_url is required for link/file material")
        return self


class MaterialOut(BaseSchema):
    id: uuid.UUID
    group_id: uuid.UUID
    title: str
    body_text: str | None = None
    type: MaterialType
    link_url: str | None = None
    is_published: bool
    created_at: datetime
    updated_at: datetime


class MaterialShortOut(BaseSchema):
    id: uuid.UUID
    group_id: uuid.UUID
    title: str
    type: MaterialType
    created_at: datetime


class MaterialsPage(BaseModel):
    items: list[MaterialOut]
    next_cursor: str | None = None


class MaterialsShortPage(BaseModel):
    items: list[MaterialShortOut]
    next_cursor: str | None = None
