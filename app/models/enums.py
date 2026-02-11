from enum import Enum


class UserType(str, Enum):
    admin = "admin"
    parent = "parent"


class LessonStatus(str, Enum):
    scheduled = "scheduled"
    cancelled = "cancelled"
    done = "done"


class NotificationStatus(str, Enum):
    queued = "queued"
    sent = "sent"
    failed = "failed"
    read = "read"


class PaymentStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class MaterialType(str, Enum):
    lecture = "lecture"
    file = "file"
    link = "link"
