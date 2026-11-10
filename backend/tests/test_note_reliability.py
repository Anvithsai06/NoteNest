import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1 import notes


class FakeDb:
    def __init__(self, commit_error: Exception | None = None, note=None):
        self.commit_error = commit_error
        self.note = note
        self.added = []
        self.deleted = []
        self.commits = 0
        self.rolled_back = False

    def add(self, value): self.added.append(value)
    def delete(self, value): self.deleted.append(value)
    def refresh(self, value): return None
    def rollback(self): self.rolled_back = True
    def commit(self):
        self.commits += 1
        if self.commit_error:
            raise self.commit_error
    def get(self, model, key): return self.note


def active_note():
    return SimpleNamespace(id=uuid4(), uploader_id=uuid4(), storage_path="drive-file-id", visibility="public", deletion_status="active", deletion_attempts=0, deletion_requested_at=None, last_deletion_error=None)


class NoteReliabilityTests(unittest.TestCase):
    def test_successful_upload_persists_after_storage(self):
        db = FakeDb()
        user = SimpleNamespace(id=uuid4(), college_name="SR University")

        async def fake_upload(*_args): return "original.pdf", "drive-file-id", 12, "application/pdf"

        with patch.object(notes, "save_upload", fake_upload):
            result = asyncio.run(notes.upload_note("Notes", "Math", None, None, None, None, user, db))
        self.assertEqual(result.storage_path, "drive-file-id")
        self.assertEqual(db.commits, 1)

    def test_storage_upload_failure_does_not_persist_database_record(self):
        db = FakeDb()
        user = SimpleNamespace(id=uuid4(), college_name="SR University")

        async def failing_upload(*_args): raise HTTPException(status_code=503, detail="storage unavailable")

        with patch.object(notes, "save_upload", failing_upload):
            with self.assertRaises(HTTPException):
                asyncio.run(notes.upload_note("Notes", "Math", None, None, None, None, user, db))
        self.assertEqual(db.added, [])

    def test_database_failure_compensates_drive_upload(self):
        db = FakeDb(SQLAlchemyError("database unavailable"))
        user = SimpleNamespace(id=uuid4(), college_name="SR University")

        async def fake_upload(*_args): return "original.pdf", "drive-file-id", 12, "application/pdf"

        with patch.object(notes, "save_upload", fake_upload), patch.object(notes, "delete_stored_file") as delete_file:
            with self.assertRaises(HTTPException) as error:
                asyncio.run(notes.upload_note("Notes", "Math", None, None, None, None, user, db))
        self.assertEqual(error.exception.status_code, 503)
        delete_file.assert_called_once_with("drive-file-id")
        self.assertTrue(db.rolled_back)

    def test_successful_pending_deletion_removes_record(self):
        note = active_note()
        db = FakeDb()
        with patch.object(notes, "delete_stored_file"):
            self.assertTrue(notes._finalize_deletion(note, db))
        self.assertEqual(db.deleted, [note])

    def test_drive_deletion_failure_remains_pending(self):
        note = active_note()
        db = FakeDb()
        with patch.object(notes, "delete_stored_file", side_effect=RuntimeError("drive unavailable")):
            self.assertFalse(notes._finalize_deletion(note, db))
        self.assertEqual(note.deletion_attempts, 1)
        self.assertEqual(note.last_deletion_error, "RuntimeError")
        self.assertEqual(db.deleted, [])

    def test_retry_deletion_retries_pending_note(self):
        note = active_note()
        note.deletion_status = "pending_deletion"
        db = FakeDb(note=note)
        user = SimpleNamespace(id=note.uploader_id)
        with patch.object(notes, "_finalize_deletion", return_value=True) as finalize:
            notes.retry_deletion(note.id, user, db)
        finalize.assert_called_once_with(note, db)

    def test_pending_note_is_not_available_to_students(self):
        note = active_note()
        note.deletion_status = "pending_deletion"
        db = FakeDb(note=note)
        with self.assertRaises(HTTPException) as error:
            notes.get_note(note.id, SimpleNamespace(), db)
        self.assertEqual(error.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
