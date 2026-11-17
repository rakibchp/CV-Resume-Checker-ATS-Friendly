from io import BytesIO
import unittest

from docx import Document
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from index import app

client = TestClient(app)


def make_text_pdf(text):
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    font_reference = writer._add_object(font)
    page[NameObject("/Resources")] = DictionaryObject(
        {
            NameObject("/Font"): DictionaryObject(
                {NameObject("/F1"): font_reference}
            )
        }
    )
    content = DecodedStreamObject()
    content.set_data(f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("ascii"))
    page[NameObject("/Contents")] = writer._add_object(content)
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


class CVCheckerTests(unittest.TestCase):
    def test_health_endpoint(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_valid_cv_response(self):
        with open("sample_cv.txt", "r", encoding="utf-8") as file:
            sample_cv = file.read()

        response = client.post("/api/validate", json={"cv_text": sample_cv})
        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertEqual(payload["total_sections"], 8)
        self.assertGreaterEqual(payload["passed_sections"], 6)
        self.assertIn("score", payload)
        self.assertEqual(payload["status"], "Excellent")
        self.assertTrue(payload["email_valid"])
        self.assertTrue(payload["phone_valid"])
        self.assertEqual(payload["ats_analysis"]["score"], 100)
        self.assertEqual(payload["ats_analysis"]["total_checks"], 10)

    def test_missing_sections_detected(self):
        with open("incomplete_cv.txt", "r", encoding="utf-8") as file:
            incomplete_cv = file.read()

        response = client.post("/api/validate", json={"cv_text": incomplete_cv})
        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertIn("Technical Skills", payload["missing_fields"])
        self.assertLess(payload["score"], 100)
        self.assertLess(payload["ats_analysis"]["score"], 100)

    def test_ats_analysis_reports_unverifiable_layout_limitations(self):
        response = client.post(
            "/api/validate",
            json={"cv_text": "Name: Test User\nEmail: test@example.com"},
        )
        self.assertEqual(response.status_code, 200)

        analysis = response.json()["ats_analysis"]
        self.assertIn("not an ATS simulation", analysis["limitation"])
        self.assertTrue(
            any("single-column" in tip for tip in analysis["recommendations"])
        )

    def test_alternative_section_names_are_accepted(self):
        cv = """
        Full Name: Test User
        Contact: +8801712345678
        Technologies: Python, FastAPI, SQL
        Career Objective
        This is a professional objective.
        Course
        B.Sc. in Computer Science
        Experience
        Worked on projects.
        References
        Available on request
        """

        response = client.post("/api/validate", json={"cv_text": cv})
        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertEqual(payload["checks"][2]["section"], "Phone Number")
        self.assertNotIn("Technical Skills", payload["missing_fields"])
        self.assertNotIn("Educational Qualification", payload["missing_fields"])

    def test_empty_cv_input_is_rejected(self):
        response = client.post("/api/validate", json={"cv_text": "   "})
        self.assertEqual(response.status_code, 422)

    def test_txt_file_upload_extracts_text(self):
        response = client.post(
            "/api/extract",
            files={"file": ("resume.txt", b"Full Name: Test User", "text/plain")},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["file_name"], "resume.txt")
        self.assertEqual(response.json()["cv_text"], "Full Name: Test User")

    def test_pdf_file_upload_extracts_text(self):
        pdf_bytes = make_text_pdf("Full Name: Test User")
        response = client.post(
            "/api/extract",
            files={"file": ("resume.pdf", pdf_bytes, "application/pdf")},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Full Name: Test User", response.json()["cv_text"])

    def test_docx_file_upload_extracts_paragraph_and_table_text(self):
        document = Document()
        document.add_paragraph("Full Name: Test User")
        table = document.add_table(rows=1, cols=1)
        table.cell(0, 0).text = "Skills: Python"
        file_buffer = BytesIO()
        document.save(file_buffer)

        response = client.post(
            "/api/extract",
            files={
                "file": (
                    "resume.docx",
                    file_buffer.getvalue(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Full Name: Test User", response.json()["cv_text"])
        self.assertIn("Skills: Python", response.json()["cv_text"])

    def test_unsupported_upload_type_is_rejected(self):
        response = client.post(
            "/api/extract",
            files={"file": ("resume.rtf", b"some text", "text/plain")},
        )

        self.assertEqual(response.status_code, 415)

    def test_upload_over_size_limit_is_rejected(self):
        response = client.post(
            "/api/extract",
            files={"file": ("resume.txt", b"a" * (5 * 1024 * 1024 + 1), "text/plain")},
        )

        self.assertEqual(response.status_code, 413)


if __name__ == "__main__":
    unittest.main()
