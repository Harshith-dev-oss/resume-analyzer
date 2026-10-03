from io import BytesIO
import tempfile
import unittest

from app import analyze_resume, app


class ResumeAnalysisTests(unittest.TestCase):
    def test_resume_analysis_reports_missing_skills_and_weak_areas(self):
        text = (
            "Python developer with 2 years of experience in SQL, pandas, and data analysis. "
            "Bachelor's degree in Computer Science. Worked on projects and built dashboards."
        )

        result = analyze_resume(text)

        self.assertIn("Python", result["skills_found"])
        self.assertIn("Machine Learning", result["missing_skills"])
        self.assertTrue(result["weak_areas"])
        self.assertTrue(result["recommendations"])


class ResumeUploadTests(unittest.TestCase):
    def setUp(self):
        self.upload_dir = tempfile.TemporaryDirectory()
        app.config["TESTING"] = True
        app.config["UPLOAD_FOLDER"] = self.upload_dir.name
        self.client = app.test_client()

    def tearDown(self):
        self.upload_dir.cleanup()

    def test_text_resume_upload_returns_analysis(self):
        response = self.client.post(
            "/",
            data={"resume": (BytesIO(b"Python developer with SQL experience"), "resume.txt")},
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Resume Analysis", response.data)

    def test_invalid_pdf_returns_error_instead_of_internal_server_error(self):
        response = self.client.post(
            "/",
            data={"resume": (BytesIO(b"not a PDF"), "resume.pdf")},
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"read that file", response.data)


if __name__ == "__main__":
    unittest.main()
