# CV Format Checker

This project is a beginner-friendly Python web application that checks whether a CV contains the basic sections expected in a standard CV format.

## Features

- Paste CV text into a textarea
- Detect required CV sections
- Calculate a compliance score
- Validate email and Bangladesh mobile numbers
- Show missing sections and improvement suggestions
- Show a separate ATS-friendly text checklist score and practical formatting tips
- Upload TXT, PDF, or DOCX CVs and review the extracted text before checking
- Use a simple FastAPI backend and a lightweight frontend

The ATS score counts ten text indicators: the eight standard section headings,
a valid email address, and a Bangladesh mobile number. It is not an ATS
simulation or a guarantee of compatibility. Pasted text cannot reveal the
original document's columns, tables, graphics, or header/footer layout.
Uploads are limited to 5 MB, and extracted CV text is limited to 20,000 characters.

## Project Structure

- `index.py` – FastAPI application and validation logic
- `public/index.html` – frontend layout
- `public/style.css` – styling
- `public/app.js` – client-side logic
- `tests/test_cv_checker.py` – automated tests
- `sample_cv.txt` – example CV with all required sections
- `incomplete_cv.txt` – example CV with missing sections

## How to Run Locally

1. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the app:
   ```bash
   python index.py
   ```

4. Open the browser at:
   ```text
   http://localhost:8000
   ```

## API Endpoint

### POST `/api/validate`

Example:

```json
{
  "cv_text": "Full Name: Ayesha Rahman\nEmail Address: ayesha@example.com\nPhone Number: +8801712345678"
}
```

The API returns a JSON response with the compliance score, missing sections, email validation result, phone validation result, and suggestions.

## Notes for Beginners

This project demonstrates a few key Python ideas:

- `lower()`, `strip()`, and `replace()` are used to clean and normalize text.
- `re.search()` helps detect email addresses and phone numbers.
- Lists and dictionaries organize the CV checks and result data.
- Functions keep the code reusable and easy to understand.
- `try` and `except` help handle errors gracefully.

## Deployment

This project is designed to work as a simple Python web app and can be adapted for deployment on Vercel or Netlify with a minimal server configuration.
