from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_user_by_id_param
from app.core.db import get_session
from app.schemas.student import StudentCreate, StudentOut
from app.services.students import create_student, list_parent_students

router = APIRouter(tags=["students"])


@router.get("/students", response_model=list[StudentOut])
async def list_students(
    user=Depends(get_user_by_id_param),
    session: AsyncSession = Depends(get_session),
):
    return await list_parent_students(session, user.id)


@router.post("/students", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
async def create_student_route(
    payload: StudentCreate,
    user=Depends(get_user_by_id_param),
    session: AsyncSession = Depends(get_session),
):
    return await create_student(
        session,
        user.id,
        payload.group_id,
        payload.first_name,
        payload.last_name,
        payload.father_name,
        payload.birthdate,
        payload.is_active,
    )
