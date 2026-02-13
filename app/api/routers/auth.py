from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_user_by_id_param
from app.core.db import get_session
from app.schemas.auth import CheckUserRequest, CheckUserResponse, LoginRequest, RegisterParentRequest
from app.schemas.course import UserCourseOut
from app.schemas.user import UserMeResponse
from app.services.auth import check_user_exists, login, register_parent
from app.services.groups import list_user_courses

router = APIRouter(tags=["auth"])


@router.post("/auth/register-parent", response_model=UserMeResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterParentRequest, session: AsyncSession = Depends(get_session)):
    user = await register_parent(
        session,
        email=payload.email,
        phone=payload.phone,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
        father_name=payload.father_name,
        timezone_str=payload.timezone,
        avatar_url=payload.avatar_url,
        child_first_name=payload.child_first_name,
        child_last_name=payload.child_last_name,
        child_father_name=payload.child_father_name,
        child_class=payload.child_class,
        group_number=payload.group_number,
    )
    return UserMeResponse(
        id=user.id,
        email=user.email,
        phone=user.phone,
        user_type=user.user_type,
        first_name=user.first_name,
        last_name=user.last_name,
        father_name=user.father_name,
        avatar_url=user.avatar_url,
        timezone=user.timezone,
        settings_json=user.settings_json,
        push_enabled=user.push_enabled,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/auth/login", response_model=UserMeResponse)
async def login_route(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    user = await login(
        session,
        email=payload.email,
        phone=payload.phone,
        password=payload.password,
    )
    return UserMeResponse(
        id=user.id,
        email=user.email,
        phone=user.phone,
        user_type=user.user_type,
        first_name=user.first_name,
        last_name=user.last_name,
        father_name=user.father_name,
        avatar_url=user.avatar_url,
        timezone=user.timezone,
        settings_json=user.settings_json,
        push_enabled=user.push_enabled,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/auth/check-user", response_model=CheckUserResponse)
async def check_user_route(payload: CheckUserRequest, session: AsyncSession = Depends(get_session)):
    user = await check_user_exists(session, payload.email, payload.phone)
    return CheckUserResponse(
        id=user.id,
        user_type=user.user_type,
        first_name=user.first_name,
        last_name=user.last_name,
        father_name=user.father_name,
    )


@router.get("/me", response_model=UserMeResponse)
async def me(user=Depends(get_user_by_id_param)):
    return UserMeResponse(
        id=user.id,
        email=user.email,
        phone=user.phone,
        user_type=user.user_type,
        first_name=user.first_name,
        last_name=user.last_name,
        father_name=user.father_name,
        avatar_url=user.avatar_url,
        timezone=user.timezone,
        settings_json=user.settings_json,
        push_enabled=user.push_enabled,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("/me/courses", response_model=list[UserCourseOut])
async def my_courses(user=Depends(get_user_by_id_param), session: AsyncSession = Depends(get_session)):
    return await list_user_courses(session, user)
