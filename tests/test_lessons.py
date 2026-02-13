from datetime import date

import pytest
from sqlalchemy import select

from app.core.security import hash_password
from app.models.group import Group
from app.models.lesson import Lesson, LessonParticipation
from app.models.student import Student
from app.models.user import User
from app.services.lessons import generate_lessons


@pytest.mark.asyncio
async def test_generate_lessons_and_will_go(session, client):
    parent_user = User(
        email="parent@example.com",
        password_hash=hash_password("password"),
        user_type="parent",
    )
    session.add(parent_user)
    await session.flush()

    group = Group(
        name="G1",
        course_title="Math",
        course_description="Basic",
        default_teacher_name="Teacher A",
        schedule_json=[
            {
                "weekday": date.today().isoweekday(),
                "start_time": "10:00",
                "duration_minutes": 60,
            }
        ],
    )
    session.add(group)
    await session.flush()

    student = Student(
        parent_user_id=parent_user.id,
        group_id=group.id,
        first_name="A",
        last_name="B",
    )
    session.add(student)
    await session.commit()

    created = await generate_lessons(session, days=1, actor_user_id=parent_user.id)
    assert created >= 1

    lesson = (await session.execute(select(Lesson).where(Lesson.group_id == group.id))).scalars().first()
    assert lesson is not None

    list_resp = await client.get(
        f"/lessons?limit=20&user_id={parent_user.id}",
    )
    assert list_resp.status_code == 200

    will_go_resp = await client.post(
        f"/lessons/{lesson.id}/will-go",
        json={"student_id": str(student.id), "will_go": True},
        params={"user_id": str(parent_user.id)},
    )
    assert will_go_resp.status_code == 200

    part = await session.get(LessonParticipation, (lesson.id, student.id))
    assert part is not None
    assert part.will_go is True
