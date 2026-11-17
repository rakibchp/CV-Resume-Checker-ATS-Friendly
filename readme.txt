# Project: CV Format Checker – Python Web Application

## 1. Project Background

I am completing an assignment for the Dhaka University IIT short course:

**Course:** Introduction to Programming and Data Analysis with Python

**Assignment:** Using Python, develop a web application prototype and deploy it to Vercel or Netlify.

**Task:** Check CV format.

I am a beginner in Python web development. Therefore, guide me through the project step by step, explain the code clearly, and help me understand the technologies and concepts used.

## 2. Project Objective

Build a web application called **CV Format Checker**.

The application should allow users to paste their CV text into a text area and check whether their CV contains the essential sections and information required by a standard CV format.

The application should analyze the submitted text and provide:

- CV format compliance score.
- List of detected sections.
- Missing sections.
- Email address validation.
- Bangladesh mobile number validation.
- Suggestions for improving CV structure.
- A clear result summary.

Important: The application checks CV structure and basic formatting requirements. It must not claim to evaluate a candidate's professional ability, employability, or actual qualifications.

## 3. Technology Stack

Use the following technologies:

### Backend
- Python 3.11+
- FastAPI
- Pydantic
- Regular Expressions (`re`)
- Python string operations

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript
- Fetch API

### Testing
- Python `unittest`
- FastAPI TestClient

### Deployment
- Vercel
- GitHub for source code management

Do not introduce unnecessary frameworks or complex architecture.

## 4. CV Requirements

The application should check for the following eight essential CV sections:

1. Full Name
2. Email Address
3. Phone Number
4. Career Objective
5. Educational Qualification
6. Technical Skills
7. Work Experience / Projects
8. References

Support common alternative headings where appropriate.

For example:

| Required section | Alternative headings |
|---|---|
| Full Name | Name, Candidate Name, Personal Information |
| Email Address | Email, E-mail, Contact Email |
| Phone Number | Mobile, Contact Number, Telephone |
| Career Objective | Objective, Professional Summary, Profile Summary |
| Educational Qualification | Education, Academic Background, Qualifications |
| Technical Skills | Skills, Core Competencies, Programming Skills |
| Work Experience / Projects | Experience, Employment History, Projects |
| References | Reference, Referees |

The checker should recognize headings regardless of capitalization.

## 5. Functional Requirements

### Feature 1: CV Text Input

- Provide a large text area.
- Allow users to paste CV text.
- Display a helpful placeholder.
- Include a Clear button.
- Include a Load Sample CV button.
- Prevent empty submissions.
- Show a character count.
- Apply a reasonable maximum input length.

### Feature 2: CV Format Analysis

When the user clicks **Check My CV**, send the text to the FastAPI backend.

The backend should:

- Normalize the submitted text.
- Check required section headings.
- Detect email addresses using regular expressions.
- Detect Bangladesh mobile numbers using regular expressions.
- Calculate the format compliance score.
- Identify missing sections.
- Generate useful improvement suggestions.

### Feature 3: Score Calculation

Use this scoring approach:

- Eight required sections.
- Each section contributes 12.5 points.
- Maximum score: 100.

Formula:

`Score = (Number of detected sections / 8) * 100`

Round the final score to the nearest whole number.

Clearly explain that this score represents CV format compliance only, not CV quality or candidate suitability.

### Feature 4: Results Dashboard

Display:

- Overall compliance score.
- Total required sections.
- Passed checks.
- Failed checks.
- Detected sections.
- Missing sections.
- Email validation result.
- Phone validation result.
- Improvement suggestions.

Use clear visual indicators for passed and failed checks.

### Feature 5: Sample CV

Provide a sample CV that users can load to test the application.

Also provide an incomplete sample CV to demonstrate how missing sections are identified.

## 6. Backend API Requirements

Create a FastAPI application with the following endpoints:

### GET `/health`

Return application health status.

### POST `/api/validate`

Accept JSON:

```json
{
  "cv_text": "Full CV text goes here"
}
```

Return structured JSON containing:

```json
{
  "total_sections": 8,
  "passed_sections": 6,
  "failed_sections": 2,
  "score": 75,
  "status": "Needs Improvement",
  "checks": [],
  "missing_fields": [],
  "suggestions": [],
  "email_valid": true,
  "phone_valid": false
}
```

You may improve the response structure if necessary, but maintain consistency between the backend, frontend, and tests.

Implement:

- Input validation.
- Meaningful error responses.
- Appropriate HTTP status codes.
- Separation of validation logic from API routing.
- Reusable Python functions.
- Clear comments for beginner understanding.

## 7. Suggested Project Structure

Use a simple and deployment-friendly structure:

```text
cv-format-checker/
│
├── index.py
├── public/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── tests/
│   └── test_cv_checker.py
│
├── requirements.txt
├── README.md
├── sample_cv.txt
├── incomplete_cv.txt
└── .gitignore
```

Keep the first version simple. Do not add a database because the application does not require persistent storage.

Ensure that the application can serve its frontend and API correctly both locally and after deployment.

## 8. Frontend Design Requirements

Build a modern, responsive, professional interface.

Design direction:

- Clean white background.
- Blue primary color.
- Light gray supporting backgrounds.
- Professional typography.
- Rounded cards.
- Clear spacing.
- Responsive layout for desktop and mobile.
- Accessible labels and buttons.
- Easy-to-read result dashboard.

The interface should include:

1. Application title and short description.
2. CV input area.
3. Sample CV button.
4. Clear button.
5. Check My CV button.
6. Loading indicator.
7. Results dashboard.
8. Missing sections list.
9. Improvement suggestions.
10. Footer with project/course information.

Do not use unnecessary animations or external UI frameworks.

## 9. Python Concepts That Must Be Demonstrated

This assignment is intended to demonstrate Python fundamentals.

Use and explain the following concepts:

### String Operations
- `lower()`
- `strip()`
- `split()`
- `find()`
- `count()`
- `replace()`
- `in`

### Regular Expressions
- `re.search()`
- `re.findall()`
- Basic email pattern matching.
- Bangladesh mobile number pattern matching.

### Python Programming
- Variables.
- Data types.
- Lists.
- Dictionaries.
- Conditional statements.
- Loops.
- Functions.
- Exception handling.
- Modules and imports.

Explain where and why each concept is used in the project.

## 10. Testing Requirements

Create automated unit tests.

Test at least these scenarios:

1. A complete CV.
2. A CV missing required sections.
3. An invalid email address.
4. An invalid Bangladesh mobile number.
5. Empty CV input.
6. CV containing alternative section headings.
7. CV containing mixed capitalization.

The tests must run using:

```bash
python -m unittest discover -s tests -v
```

Fix any failing tests before declaring the project complete.

## 11. Deployment Requirements

Prepare the application for Vercel deployment.

Provide:

- Correct Vercel-compatible FastAPI entry point.
- Required Python dependencies.
- Static frontend configuration.
- GitHub repository setup instructions.
- Vercel deployment instructions.
- Environment configuration if required.
- Troubleshooting for common deployment errors.

Verify the current Vercel deployment requirements before finalizing the configuration.

The application must work at its deployed public URL, including both the frontend and `/api/validate` endpoint.

If Vercel does not support a particular implementation detail, explain the limitation and provide a working alternative rather than pretending deployment succeeded.

## 12. README.md Requirements

Generate a professional README.md containing:

1. Project title.
2. Project description.
3. Assignment background.
4. Objectives.
5. Technology stack.
6. Features.
7. Project directory structure.
8. Installation instructions.
9. Local execution instructions.
10. API documentation.
11. Testing instructions.
12. Deployment instructions.
13. Python concepts demonstrated.
14. Limitations.
15. Future improvements.

Include example commands that work on macOS and Windows where relevant.

## 13. Step-by-Step Learning Instructions

Do not generate the entire project and leave me without explanations.

Guide me through these stages:

### Stage 1: Project Understanding
- Explain the problem.
- Explain the proposed solution.
- Explain the architecture.
- Explain how frontend and backend communicate.

### Stage 2: Python Environment
- Check Python installation.
- Create a virtual environment.
- Activate the virtual environment.
- Install dependencies.

### Stage 3: Backend Development
- Create the FastAPI application.
- Implement CV text analysis.
- Implement section detection.
- Implement email and phone validation.
- Implement score calculation.
- Explain every important function.

### Stage 4: Frontend Development
- Build the HTML page.
- Add responsive CSS.
- Implement JavaScript functionality.
- Connect the frontend to the API.

### Stage 5: Testing
- Write unit tests.
- Run the tests.
- Fix errors.
- Test the API and frontend manually.

### Stage 6: GitHub
- Create a repository.
- Initialize Git.
- Commit the project.
- Push the source code to GitHub.

### Stage 7: Vercel Deployment
- Import the GitHub repository.
- Configure deployment.
- Deploy the application.
- Verify the live website and API.

### Stage 8: Assignment Preparation
Prepare:
- Project overview.
- System architecture explanation.
- Python concepts used.
- Main feature descriptions.
- Testing evidence.
- Deployment evidence.
- A short presentation script for explaining the project to the instructor.

## 14. Code Quality Requirements

Follow these rules:

- Write clean and readable Python code.
- Use meaningful variable and function names.
- Avoid unnecessary complexity.
- Keep functions small and reusable.
- Handle invalid input safely.
- Avoid hardcoded frontend results.
- Do not use fake API responses.
- Do not claim deployment or tests succeeded unless verified.
- Keep dependencies minimal.
- Ensure all code files are complete.
- Ensure imports and file paths are correct.
- Maintain consistency between frontend, backend, and tests.

## 15. Expected Final Deliverables

At the end, provide:

1. Complete working source code.
2. Full project folder structure.
3. All required frontend files.
4. All required backend files.
5. Unit tests.
6. Sample CV files.
7. requirements.txt.
8. README.md.
9. Vercel deployment configuration.
10. A downloadable ZIP archive if file-generation tools are available.
11. GitHub publishing instructions.
12. Vercel deployment instructions.
13. Final assignment presentation notes.

If you can create files, create the actual files rather than displaying only code snippets. Verify that the ZIP archive exists and contains every required file before sharing its download link.

## 16. How You Should Work With Me

Act as my Python instructor and software development mentor.

I am a beginner in Python web application development.

- Explain each stage in simple language.
- Show the exact terminal commands.
- Explain where to create each file.
- Provide complete code, not incomplete fragments.
- Explain how to run and verify each stage.
- Wait for my confirmation before moving to the next stage when working interactively.
- If I encounter an error, diagnose it before suggesting changes.
- Do not assume I already understand FastAPI, APIs, regular expressions, or deployment.

**Start by explaining the project architecture and Stage 1. Do not skip directly to deployment.**