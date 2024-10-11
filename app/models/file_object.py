# app/models/file_object.py
import uuid

from mongoengine import Document, BooleanField, UUIDField
from app.models.encrypted_string_field import EncryptedStringField


class FileObject(Document):
    """FileObject model for storing file objects."""

    file_uuid = UUIDField(default=uuid.uuid4, primary_key=True)
    file_type = EncryptedStringField(required=True, choices=['image', 'video', 'audio', 'document'])
    name = EncryptedStringField(required=True)
    base64 = EncryptedStringField(required=True)
    compressed = BooleanField(required=True)

    meta = {'collection': 'file_object'}
