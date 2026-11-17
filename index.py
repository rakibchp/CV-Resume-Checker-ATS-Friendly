import re
from io import BytesIO
from pathlib import Path
from typing import Dict, List
from zipfile import BadZipFile

from docx import Document
from docx.opc.exceptions import PackageNotFoundError
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from pypdf import PdfReader
from pypdf.errors import PdfReadError

BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"
MAX_CV_TEXT_LENGTH = 20000
MAX_UPLOAD_BYTES = 5 * 1024 * 1024

app = FastAPI(title="CV Format Checker", version="1.0.0")
app.mount("/public", StaticFiles(directory=str(PUBLIC_DIR)), name="public")

SECTION_RULES = [
    {
        "name": "Full Name",
        "aliases": ["full name", "name", "candidate name", "personal information"],
    },
    {
        "name": "Email Address",
        "aliases": ["email address", "email", "e-mail", "contact email"],
    },
    {
        "name": "Phone Number",
        "aliases": [
            "phone number",
            "mobile",
            "contact",
            "cell",
            "contact number",
            "telephone",
        ],
    },
    {
        "name": "Career Objective",
        "aliases": ["career objective", "objective", "professional summary", "profile summary"],
    },
    {
        "name": "Educational Qualification",
        "aliases": [
            "educational qualification",
            "education",
            "academic background",
            "qualifications",
            "course",
            "courses",
            "training",
            "short course",
        ],
    },
    {
        "name": "Technical Skills",
        "aliases": [
            "technical skills",
            "skills",
            "technologies",
            "core competencies",
            "programming skills",
        ],
    },
    {
        "name": "Work Experience / Projects",
        "aliases": [
            "work experience",
            "experience",
            "employment history",
            "projects",
            "project experience",
        ],
    },
    {
        "name": "References",
        "aliases": ["references", "reference", "referees"],
    },
]

EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
BANGLADESH_PHONE_PATTERN = r"(?:\+?88)?01[3-9]\d{8}\b"


class CVRequest(BaseModel):
    cv_text: str = Field(
        ..., min_length=1, max_length=MAX_CV_TEXT_LENGTH, description="Full CV text"
    )

    @field_validator("cv_text")
    @classmethod
    def validate_cv_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("CV text cannot be empty.")
        return cleaned


def normalize_text(text: str) -> str:
    """Convert the CV text to a consistent format for checking."""
    text = text.strip()
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    return text


def extract_cv_text(filename: str, file_bytes: bytes) -> str:
    """Extract readable text from a supported CV file."""
    extension = Path(filename).suffix.lower()

    if extension == ".txt":
        try:
            return file_bytes.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise HTTPException(
                status_code=422, detail="Text files must use UTF-8 encoding."
            ) from exc

    if extension == ".pdf":
        try:
            pdf = PdfReader(BytesIO(file_bytes), strict=False)
            if pdf.is_encrypted:
                raise HTTPException(
                    status_code=422, detail="Password-protected PDF files are not supported."
                )
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
        except (PdfReadError, ValueError) as exc:
            raise HTTPException(
                status_code=422, detail="The PDF could not be read. Try another PDF file."
            ) from exc

    if extension == ".docx":
        try:
            document = Document(BytesIO(file_bytes))
        except (PackageNotFoundError, BadZipFile, ValueError) as exc:
            raise HTTPException(
                status_code=422, detail="The DOCX file could not be read. Try another file."
            ) from exc

        text_parts = [paragraph.text for paragraph in document.paragraphs]
        for table in document.tables:
            for row in table.rows:
                text_parts.append("  ".join(cell.text for cell in row.cells))
        return "\n".join(text_parts)

    raise HTTPException(
        status_code=415, detail="Unsupported file type. Upload a TXT, PDF, or DOCX file."
    )


def detect_email_address(text: str) -> bool:
    """Check whether the text contains a valid email address pattern."""
    return bool(re.search(EMAIL_PATTERN, text, flags=re.IGNORECASE))


def detect_bangladesh_mobile(text: str) -> bool:
    """Check if the text contains a valid Bangladesh mobile number."""
    return bool(re.search(BANGLADESH_PHONE_PATTERN, text))


def detect_sections(cv_text: str) -> List[str]:
    """Find which required CV sections are present in the text."""
    text = normalize_text(cv_text).lower()
    detected: List[str] = []

    for section in SECTION_RULES:
        pattern_parts = [re.escape(item) for item in section["aliases"]]
        heading_pattern = r"(?im)^\s*(?:" + "|".join(pattern_parts) + r")\s*[:\-]?\s*(?:.*)$"
        if re.search(heading_pattern, text):
            detected.append(section["name"])

    return detected


def build_suggestions(missing_fields: List[str], email_valid: bool, phone_valid: bool) -> List[str]:
    """Provide helpful suggestions for improving the CV structure."""
    suggestions: List[str] = []

    if missing_fields:
        for field in missing_fields:
            suggestions.append(f"Add a '{field}' section so the CV is easier to review.")

    if not email_valid:
        suggestions.append("Add a valid email address, for example name@example.com.")

    if not phone_valid:
        suggestions.append("Add a valid Bangladesh mobile number, such as +88017XXXXXXXX.")

    if not suggestions:
        suggestions.append("Your CV structure looks good. Keep the headings clear and consistent.")

    return suggestions


def build_ats_analysis(
    detected_sections: List[str], email_valid: bool, phone_valid: bool
) -> Dict[str, object]:
    """Score text-based ATS indicators without claiming to test the original layout."""
    ats_checks = [
        {
            "name": f"Standard heading: {section['name']}",
            "passed": section["name"] in detected_sections,
        }
        for section in SECTION_RULES
    ]
    ats_checks.extend(
        [
            {"name": "Valid email address", "passed": email_valid},
            {"name": "Bangladesh mobile number", "passed": phone_valid},
        ]
    )

    passed_checks = sum(check["passed"] for check in ats_checks)
    total_checks = len(ats_checks)
    recommendations = [
        f"Use a standard heading for '{section['name']}'."
        for section in SECTION_RULES
        if section["name"] not in detected_sections
    ]

    if not email_valid:
        recommendations.append("Add a valid email address in the CV text.")
    if not phone_valid:
        recommendations.append("Add a valid Bangladesh mobile number in the CV text.")

    recommendations.extend(
        [
            "Keep the original document in a simple, single-column layout; avoid tables, text boxes, and graphics.",
            "Keep contact information in the document body rather than a header or footer.",
            "Tailor relevant skills and terms to each job description; this checker does not compare keywords.",
        ]
    )

    return {
        "score": round((passed_checks / total_checks) * 100),
        "passed_checks": passed_checks,
        "total_checks": total_checks,
        "checks": ats_checks,
        "recommendations": recommendations,
        "limitation": (
            "This is a text-based checklist, not an ATS simulation. Pasted text cannot show "
            "whether the original file uses columns, tables, graphics, or headers and footers."
        ),
    }


def validate_cv(cv_text: str) -> Dict[str, object]:
    """Run all CV structure checks and return a result dictionary."""
    normalized_text = normalize_text(cv_text)
    detected_sections = detect_sections(normalized_text)

    total_sections = len(SECTION_RULES)
    passed_sections = len(detected_sections)
    failed_sections = total_sections - passed_sections
    score = round((passed_sections / total_sections) * 100)

    missing_fields = [
        section["name"]
        for section in SECTION_RULES
        if section["name"] not in detected_sections
    ]

    email_valid = detect_email_address(normalized_text)
    phone_valid = detect_bangladesh_mobile(normalized_text)

    if score >= 85:
        status = "Excellent"
    elif score >= 70:
        status = "Good"
    elif score >= 50:
        status = "Needs Improvement"
    else:
        status = "Poor"

    checks = []
    for section in SECTION_RULES:
        present = section["name"] in detected_sections
        checks.append(
            {
                "section": section["name"],
                "status": "passed" if present else "failed",
                "present": present,
            }
        )

    return {
        "total_sections": total_sections,
        "passed_sections": passed_sections,
        "failed_sections": failed_sections,
        "score": score,
        "status": status,
        "checks": checks,
        "missing_fields": missing_fields,
        "suggestions": build_suggestions(missing_fields, email_valid, phone_valid),
        "email_valid": email_valid,
        "phone_valid": phone_valid,
        "ats_analysis": build_ats_analysis(
            detected_sections, email_valid, phone_valid
        ),
    }


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Return the health state of the application."""
    return {"status": "ok"}


@app.get("/")
def home() -> FileResponse:
    """Serve the main frontend page."""
    return FileResponse(PUBLIC_DIR / "index.html")


@app.get("/sample_cv.txt")
def sample_cv() -> FileResponse:
    """Return a complete sample CV for testing the app."""
    return FileResponse(BASE_DIR / "sample_cv.txt")


@app.get("/incomplete_cv.txt")
def incomplete_cv() -> FileResponse:
    """Return an incomplete sample CV to show missing sections."""
    return FileResponse(BASE_DIR / "incomplete_cv.txt")


@app.post("/api/validate")
def validate_api(payload: CVRequest) -> Dict[str, object]:
    """Validate the submitted CV and return a result summary."""
    try:
        result = validate_cv(payload.cv_text)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"CV validation failed: {str(exc)}") from exc


@app.post("/api/extract")
async def extract_uploaded_cv(file: UploadFile = File(...)) -> Dict[str, str]:
    """Extract CV text from a user-uploaded TXT, PDF, or DOCX file."""
    try:
        filename = file.filename or ""
        if Path(filename).suffix.lower() not in {".txt", ".pdf", ".docx"}:
            raise HTTPException(
                status_code=415,
                detail="Unsupported file type. Upload a TXT, PDF, or DOCX file.",
            )

        file_bytes = await file.read(MAX_UPLOAD_BYTES + 1)
        if not file_bytes:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")
        if len(file_bytes) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413, detail="The uploaded file must be 5 MB or smaller."
            )

        cv_text = extract_cv_text(filename, file_bytes).strip()
        if not cv_text:
            raise HTTPException(
                status_code=422,
                detail="No readable text was found in the file. Try a text-based PDF, DOCX, or TXT.",
            )
        if len(cv_text) > MAX_CV_TEXT_LENGTH:
            raise HTTPException(
                status_code=413,
                detail=f"Extracted CV text must be {MAX_CV_TEXT_LENGTH} characters or fewer.",
            )

        return {"file_name": Path(filename).name, "cv_text": cv_text}
    finally:
        await file.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("index:app", host="0.0.0.0", port=8000, reload=True)
