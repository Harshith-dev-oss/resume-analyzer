import unittest

from app import analyze_resume


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


if __name__ == "__main__":
    unittest.main()
