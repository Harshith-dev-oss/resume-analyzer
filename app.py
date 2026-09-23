import os
import re
from collections import Counter

from docx import Document
from flask import Flask, render_template, request
from pypdf import PdfReader
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

SKILLS = [
    "Python",
    "Flask",
    "JavaScript",
    "React",
    "Node.js",
    "SQL",
    "PostgreSQL",
    "MongoDB",
    "API",
    "REST",
    "Git",
    "Docker",
    "AWS",
    "Machine Learning",
    "Data Analysis",
    "Excel",
    "Tableau",
    "Power BI",
    "NLP",
    "Pandas",
    "NumPy",
    "Java",
    "C++",
    "HTML",
    "CSS",
    "TypeScript",
    "Project Management",
]

SKILL_GROUPS = {
    "Data & Analytics": ["SQL", "Data Analysis", "Excel", "Power BI", "Tableau", "Pandas", "NumPy"],
    "Web Development": ["JavaScript", "React", "HTML", "CSS", "TypeScript", "Node.js"],
    "Backend & APIs": ["Python", "Flask", "Node.js", "API", "REST", "Java"],
    "Cloud & DevOps": ["Git", "Docker", "AWS"],
    "AI / ML": ["Machine Learning", "NLP", "Python", "Pandas", "NumPy"],
    "Product / Leadership": ["Project Management"],
}

PRIORITY_SKILLS = [
    "Python",
    "SQL",
    "Machine Learning",
    "React",
    "Docker",
    "AWS",
    "API",
    "Power BI",
    "Data Analysis",
    "Git",
    "Flask",
    "JavaScript",
    "Project Management",
    "NLP",
    "Tableau",
]


def extract_text(file_path):
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        reader = PdfReader(file_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text

    if extension == ".docx":
        doc = Document(file_path)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)

    if extension in {".txt", ".md"}:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            return file.read()

    raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")


def analyze_resume(text):
    cleaned = text or ""
    lower_text = cleaned.lower()

    skills_found = []
    for skill in SKILLS:
        if skill.lower() in lower_text:
            skills_found.append(skill)

    priority_missing = [skill for skill in PRIORITY_SKILLS if skill not in skills_found]
    remaining_missing = [skill for skill in SKILLS if skill not in skills_found and skill not in priority_missing]
    missing_skills = (priority_missing + remaining_missing)[:10]

    weak_areas = []
    for group_name, group_skills in SKILL_GROUPS.items():
        detected = [skill for skill in group_skills if skill in skills_found]
        if len(detected) == 0:
            weak_areas.append(group_name)
        elif len(detected) == 1 and len(group_skills) > 2:
            weak_areas.append(f"{group_name} (limited coverage)")

    recommendations = []
    for skill in missing_skills:
        if skill in ["Python", "SQL", "Machine Learning", "React", "Docker", "AWS", "API", "Power BI"]:
            recommendations.append(f"Add more hands-on experience in {skill} to strengthen your profile.")

    if not recommendations:
        recommendations.append("Your resume already shows a strong mix of core skills. Consider adding leadership or project-impact details.")

    if not weak_areas:
        weak_areas = ["Overall skill coverage looks balanced. No major gap detected."]

    experience_years = re.findall(r"\b\d+\s*(?:to\s*\d+\s*)?years?\b", cleaned, flags=re.IGNORECASE)
    education_mentions = bool(re.search(r"\b(bachelor|master|degree|b\.sc|m\.sc|phd)\b", lower_text))
    projects_mentions = bool(re.search(r"\b(projects?|portfolio|experience)\b", lower_text))

    score = 35
    score += min(len(skills_found) * 8, 40)
    if experience_years:
        score += 10
    if education_mentions:
        score += 10
    if projects_mentions:
        score += 5

    score = min(score, 100)

    if score >= 85:
        status = "Strong fit"
    elif score >= 65:
        status = "Good match"
    elif score >= 45:
        status = "Moderate match"
    else:
        status = "Needs improvement"

    word_count = len(re.findall(r"\b\w+\b", cleaned))
    summary = (
        f"This resume includes {len(skills_found)} key skill matches, "
        f"{word_count} words, and a {status.lower()} profile for the target role."
    )

    return {
        "skills_found": skills_found,
        "missing_skills": missing_skills,
        "weak_areas": weak_areas,
        "recommendations": recommendations,
        "match_score": score,
        "status": status,
        "word_count": word_count,
        "experience_years": experience_years,
        "summary": summary,
    }


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("resume")
        if not file or file.filename == "":
            return render_template("index.html", error="Please upload a resume file.")

        filename = secure_filename(file.filename)
        if not filename:
            return render_template("index.html", error="Invalid filename.")

        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        try:
            text = extract_text(file_path)
            results = analyze_resume(text)
            return render_template("result.html", filename=filename, results=results)
        except ValueError as exc:
            return render_template("index.html", error=str(exc))

    return render_template("index.html", error=None)


@app.route("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
