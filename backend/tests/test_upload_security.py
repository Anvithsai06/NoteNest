import io
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from fastapi import HTTPException, UploadFile

from app.services import file_service, malware_scanner


class UploadSecurityTests(unittest.TestCase):
    def test_detects_pdf_png_jpeg_and_rejects_mismatch(self):
        self.assertEqual(file_service.detect_mime_type(b"%PDF-1.7", ".pdf"), "application/pdf")
        self.assertEqual(file_service.detect_mime_type(b"\x89PNG\r\n\x1a\nbody", ".png"), "image/png")
        self.assertEqual(file_service.detect_mime_type(b"\xff\xd8\xffbody", ".jpg"), "image/jpeg")
        with self.assertRaises(HTTPException):
            file_service.detect_mime_type(b"not-a-pdf", ".pdf")

    def test_detects_ooxml_and_rejects_invalid_archive(self):
        buffer = io.BytesIO()
        with ZipFile(buffer, "w") as archive:
            archive.writestr("[Content_Types].xml", "<Types />")
            archive.writestr("word/document.xml", "<document />")
        self.assertIn("wordprocessingml", file_service.detect_mime_type(buffer.getvalue(), ".docx"))
        with self.assertRaises(HTTPException):
            file_service.detect_mime_type(b"not-a-zip", ".docx")

    def test_required_scanner_cannot_be_disabled(self):
        with patch.object(malware_scanner.settings, "malware_scanning_enabled", False), patch.object(malware_scanner.settings, "malware_scanning_required", True):
            with self.assertRaises(HTTPException) as error:
                malware_scanner.scan_bytes(b"test")
        self.assertEqual(error.exception.status_code, 503)

    def test_scanner_reports_infected_file(self):
        class FakeSocket:
            def __enter__(self): return self
            def __exit__(self, *_args): return False
            def sendall(self, _data): pass
            def recv(self, _size): return b"stream: Eicar-Test-Signature FOUND\0"

        with patch.object(malware_scanner.settings, "malware_scanning_enabled", True), patch.object(malware_scanner.settings, "malware_scanning_required", True), patch("app.services.malware_scanner.socket.create_connection", return_value=FakeSocket()):
            with self.assertRaises(HTTPException) as error:
                malware_scanner.scan_bytes(b"test")
        self.assertEqual(error.exception.status_code, 415)

    def test_scanner_readiness_ping(self):
        class FakeSocket:
            def __enter__(self): return self
            def __exit__(self, *_args): return False
            def sendall(self, _data): pass
            def recv(self, _size): return b"PONG\0"

        with patch("app.services.malware_scanner.socket.create_connection", return_value=FakeSocket()):
            self.assertTrue(malware_scanner.scanner_ready())


if __name__ == "__main__":
    unittest.main()
