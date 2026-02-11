import uuid

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.schemas.common import BaseSchema


class RegisterParentRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    password: str = Field(min_length=6)
    first_name: str | None = None
    last_name: str | None = None
    father_name: str | None = None
    timezone: str | None = "Europe/Vienna"
    avatar_url: str | None = None

    @model_validator(mode="after")
    def validate_contact(self):
        if not self.email and not self.phone:
            raise ValueError("email or phone is required")
        return self


class LoginRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    password: str = Field(min_length=6)

    @model_validator(mode="after")
    def validate_contact(self):
        if not self.email and not self.phone:
            raise ValueError("email or phone is required")
        return self


class CheckUserRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None

    @model_validator(mode="after")
    def validate_contact(self):
        if not self.email and not self.phone:
            raise ValueError("email or phone is required")
        return self


class CheckUserResponse(BaseSchema):
    id: uuid.UUID
    user_type: str
    first_name: str | None = None
    last_name: str | None = None
    father_name: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_expires_in: int
