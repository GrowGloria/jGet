from datetime import datetime, timedelta, timezone
import uuid

import pytest

from app.core.security import create_access_token, hash_password
from app.models.group import Group
from app.models.lesson import Lesson
from app.models.manager import Manager
from app.models.student import Student
from app.models.user import User


@pytest.mark.asyncio
async def test_auth_check_user_found_and_missing(session, client):
    email = f"check-{uuid.uuid4().hex}@example.com"
    user = User(
        email=email,
        password_hash=hash_password("password"),
        user_type="parent",
    )
    session.add(user)
    await session.commit()

    found_resp = await client.post("/auth/check-user", json={"email": email})
    assert found_resp.status_code == 200
    found = found_resp.json()
    assert found["id"] == str(user.id)
    assert found["user_type"] == "parent"
    assert "password_hash" not in found

    missing_resp = await client.post("/auth/check-user", json={"email": f"missing-{uuid.uuid4().hex}@example.com"})
    assert missing_resp.status_code == 403
    assert missing_resp.json()["error"]["code"] == "AUTH_USER_NOT_FOUND"


@pytest.mark.asyncio
async def test_lessons_pagination_and_detail(session, client):
    parent = User(
        email=f"parent-{uuid.uuid4().hex}@example.com",
        password_hash=hash_password("password"),
        user_type="parent",
    )
    session.add(parent)
    await session.flush()

    group = Group(
        name="Group A",
        course_title="Math",
        course_description="Basics",
        schedule_json=[],
    )
    session.add(group)
    await session.flush()

    student = Student(
        parent_user_id=parent.id,
        group_id=group.id,
        first_name="A",
        last_name="B",
    )
    session.add(student)

    starts_first = datetime(2025, 1, 2, 10, 0, tzinfo=timezone.utc)
    ends_first = starts_first + timedelta(minutes=90)
    starts_second = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
    ends_second = starts_second + timedelta(minutes=60)

    lesson_first = Lesson(
        group_id=group.id,
        starts_at=starts_first,
        ends_at=ends_first,
        topic="Topic 1",
        plan_text="Plan 1",
        teacher_name="Teacher",
        cabinet_text="Room 1",
        status="scheduled",
    )
    lesson_second = Lesson(
        group_id=group.id,
        starts_at=starts_second,
        ends_at=ends_second,
        topic="Topic 2",
        plan_text="Plan 2",
        teacher_name="Teacher",
        cabinet_text="Room 1",
        status="scheduled",
    )
    session.add_all([lesson_first, lesson_second])
    await session.commit()

    token = create_access_token(parent.id)

    page_one = await client.get(
        "/lessons?limit=1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert page_one.status_code == 200
    page_one_data = page_one.json()
    assert page_one_data["items"][0]["id"] == str(lesson_first.id)
    assert page_one_data["next_cursor"]

    page_two = await client.get(
        f"/lessons?limit=1&cursor={page_one_data['next_cursor']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert page_two.status_code == 200
    page_two_data = page_two.json()
    assert page_two_data["items"][0]["id"] == str(lesson_second.id)

    detail = await client.get(
        f"/lessons/{lesson_first.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail.status_code == 200
    detail_data = detail.json()
    assert detail_data["duration_minutes"] == 90
    assert detail_data["title"] == "Topic 1"


@pytest.mark.asyncio
async def test_me_courses(session, client):
    parent = User(
        email=f"courses-{uuid.uuid4().hex}@example.com",
        password_hash=hash_password("password"),
        user_type="parent",
    )
    session.add(parent)
    await session.flush()

    group = Group(
        name="Group Courses",
        course_title="Biology",
        course_description="Intro",
        schedule_json=[],
    )
    session.add(group)
    await session.flush()

    student = Student(
        parent_user_id=parent.id,
        group_id=group.id,
        first_name="C",
        last_name="D",
    )
    session.add(student)
    await session.commit()

    token = create_access_token(parent.id)
    resp = await client.get(
        "/me/courses",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    courses = resp.json()
    assert any(item["group_id"] == str(group.id) for item in courses)


@pytest.mark.asyncio
async def test_managers_list(session, client):
    user = User(
        email=f"manager-{uuid.uuid4().hex}@example.com",
        password_hash=hash_password("password"),
        user_type="parent",
    )
    manager = Manager(
        first_name="Ivan",
        last_name="Petrov",
        father_name="Sergeevich",
        telegram_url="https://t.me/example",
        whatsapp_url="https://wa.me/123",
    )
    session.add_all([user, manager])
    await session.commit()

    token = create_access_token(user.id)
    resp = await client.get(
        "/managers",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert any(item["id"] == str(manager.id) for item in data)
