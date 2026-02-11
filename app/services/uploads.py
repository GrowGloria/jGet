import os
import uuid

from fastapi import UploadFile

from app.core.settings import settings


async def save_upload(upload: UploadFile) -> str:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = ""
    if upload.filename and "." in upload.filename:
        ext = "." + upload.filename.split(".")[-1]
    storage_key = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(settings.UPLOAD_DIR, storage_key)

    content = await upload.read()
    with open(path, "wb") as f:
        f.write(content)

    return f"/uploads/{storage_key}"
