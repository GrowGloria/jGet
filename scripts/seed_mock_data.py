import argparse
import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select

from app.core.db import AsyncSessionLocal
from app.core.security import hash_password
from app.models.device_token import DeviceToken
from app.models.group import Group
from app.models.lesson import Lesson, LessonParticipation
from app.models.manager import Manager
from app.models.material import Material
from app.models.notification import Notification
from app.models.payment import Payment
from app.models.student import Student
from app.models.user import User


async def _clear_data():
    async with AsyncSessionLocal() as session:
        for model in (
            LessonParticipation,
            Payment,
            Notification,
            DeviceToken,
            Material,
            Lesson,
            Student,
            Group,
            Manager,
            User,
        ):
            await session.execute(delete(model))
        await session.commit()


async def _seed():
    async with AsyncSessionLocal() as session:
        existing = (await session.execute(select(User).limit(1))).scalar_one_or_none()
        if existing:
            print("Data already exists. Use --reset to clear and reseed.")
            return

        admin = User(
            email="admin@example.com",
            phone="+10000000000",
            password_hash=hash_password("admin123"),
            user_type="admin",
            first_name="Admin",
            last_name="User",
            father_name=None,
            timezone="Europe/Vienna",
            settings_json={},
            push_enabled=True,
        )
        parent_one = User(
            email="parent1@example.com",
            phone="+10000000001",
            password_hash=hash_password("parent123"),
            user_type="parent",
            first_name="Ivan",
            last_name="Petrov",
            father_name="Sergeevich",
            timezone="Europe/Vienna",
            settings_json={},
            push_enabled=True,
        )
        parent_two = User(
            email="parent2@example.com",
            phone="+10000000002",
            password_hash=hash_password("parent123"),
            user_type="parent",
            first_name="Anna",
            last_name="Sokolova",
            father_name="Igorevna",
            timezone="Europe/Vienna",
            settings_json={},
            push_enabled=True,
        )
        session.add_all([admin, parent_one, parent_two])
        await session.flush()

        group_one = Group(
            name="G-001",
            course_title="Math",
            course_description="Basic arithmetic",
            default_teacher_name="Mr. Smith",
            capacity=12,
            is_active=True,
            schedule_json=[{"weekday": 1, "start_time": "10:00", "duration_minutes": 60, "cabinet_text": "101"}],
        )
        group_two = Group(
            name="G-002",
            course_title="Biology",
            course_description="Intro to biology",
            default_teacher_name="Ms. Lee",
            capacity=10,
            is_active=True,
            schedule_json=[{"weekday": 3, "start_time": "15:30", "duration_minutes": 90, "cabinet_text": "202"}],
        )
        session.add_all([group_one, group_two])
        await session.flush()

        student_one = Student(
            parent_user_id=parent_one.id,
            group_id=group_one.id,
            first_name="Pavel",
            last_name="Petrov",
            father_name="Ivanovich",
            school_class="5A",
            group_number=group_one.name,
            is_active=True,
        )
        student_two = Student(
            parent_user_id=parent_two.id,
            group_id=group_two.id,
            first_name="Olga",
            last_name="Sokolova",
            father_name="Andreevna",
            school_class="6B",
            group_number=group_two.name,
            is_active=True,
        )
        session.add_all([student_one, student_two])
        await session.flush()

        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        lessons = []
        for idx in range(3):
            start_one = now + timedelta(days=idx + 1, hours=2)
            lessons.append(
                Lesson(
                    group_id=group_one.id,
                    starts_at=start_one,
                    ends_at=start_one + timedelta(minutes=60),
                    topic=f"Math lesson {idx + 1}",
                    plan_text="Practice and exercises",
                    teacher_name=group_one.default_teacher_name,
                    cabinet_text="101",
                    status="scheduled",
                )
            )
            start_two = now + timedelta(days=idx + 1, hours=5)
            lessons.append(
                Lesson(
                    group_id=group_two.id,
                    starts_at=start_two,
                    ends_at=start_two + timedelta(minutes=90),
                    topic=f"Biology lesson {idx + 1}",
                    plan_text="Intro topics",
                    teacher_name=group_two.default_teacher_name,
                    cabinet_text="202",
                    status="scheduled",
                )
            )
        session.add_all(lessons)
        await session.flush()

        session.add(
            LessonParticipation(
                lesson_id=lessons[0].id,
                student_id=student_one.id,
                will_go=True,
            )
        )

        materials = [
            Material(
                group_id=group_one.id,
                title="Math workbook",
                body_text="Workbook PDF for week 1",
                type="lecture",
                link_url="https://example.com/math-workbook",
                is_published=True,
            ),
            Material(
                group_id=group_two.id,
                title="Biology slides",
                body_text="Slides for the intro lesson",
                type="presentation",
                link_url="https://example.com/bio-slides",
                is_published=True,
            ),
        ]
        session.add_all(materials)

        notifications = [
            Notification(
                user_id=parent_one.id,
                type="lesson_reminder",
                title="Lesson reminder",
                body="Math lesson starts soon",
                payload={"lesson_id": str(lessons[0].id), "group_id": str(group_one.id)},
                status="queued",
                scheduled_at=now,
            ),
            Notification(
                user_id=parent_two.id,
                type="announcement",
                title="New materials",
                body="Biology slides are available",
                payload={"group_id": str(group_two.id)},
                status="sent",
                sent_at=now,
            ),
        ]
        session.add_all(notifications)

        payment = Payment(
            parent_user_id=parent_one.id,
            student_id=student_one.id,
            group_id=group_one.id,
            lesson_id=lessons[0].id,
            amount_cents=1500,
            currency="EUR",
            provider="mock",
            provider_payment_id="mock-001",
            status="paid",
            paid_at=now,
        )
        session.add(payment)

        device_token = DeviceToken(
            user_id=parent_one.id,
            token="device-token-parent-1",
            platform="ios",
        )
        session.add(device_token)

        manager = Manager(
            first_name="Elena",
            last_name="Ivanova",
            father_name="Petrovna",
            telegram_url="https://t.me/example_manager",
            whatsapp_url="https://wa.me/10000000000",
        )
        session.add(manager)

        await session.commit()

        print("Seed completed.")
        print(f"Admin user id: {admin.id}")
        print(f"Parent 1 id: {parent_one.id}")
        print(f"Parent 2 id: {parent_two.id}")
        print(f"Group 1 id: {group_one.id}")
        print(f"Group 2 id: {group_two.id}")
        print(f"Student 1 id: {student_one.id}")
        print(f"Student 2 id: {student_two.id}")


def main():
    parser = argparse.ArgumentParser(description="Seed mock data into the database.")
    parser.add_argument("--reset", action="store_true", help="Clear existing data before seeding.")
    args = parser.parse_args()

    async def _run():
        if args.reset:
            await _clear_data()
        await _seed()

    asyncio.run(_run())


if __name__ == "__main__":
    main()
