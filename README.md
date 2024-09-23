# Resume Parser

## Overview
This project is a robust resume parsing system capable of extracting key information from PDF resumes. It features a user-friendly frontend interface for uploading resumes and viewing extracted data, coupled with a powerful backend for processing and storing the parsed information.

## Features
- Upload PDF resumes
- Extract key information including:
  - Name
  - Phone Number
  - Email Address
  - Education (institutions and timeframes)
  - Work Experience (companies and durations)
  - Technologies/Skills
- Asynchronous parsing for improved performance
- RESTful API for resume upload and data retrieval
- User-friendly frontend for interaction with the system

## Tech Stack
### Backend
- Django
- Django Rest Framework (DRF)
- Celery (for asynchronous tasks)
- Redis (as message broker and result backend)
- PyPDF2 (for PDF reading)
- spaCy (for natural language processing)

### Frontend
- HTML/CSS/JavaScript
- jQuery (for AJAX requests)

### DevOps
- Docker (for containerization)
- GitLab CI/CD (for continuous integration and deployment - yet to be implemented)

## Setup and Installation
1. Clone the repository:
   ```
   git clone https://gitlab.com/iot8283314/resume-parsing-application.git
   cd resume-parsing-application
   ```

2. Pull, build and run the Docker containers:
   ```
   docker run -p 8000:8000 aashishnandakumar/resume-parser:latest
   ```

3. Access the application at `http://localhost:8000`

## Usage
1. Navigate to the homepage
2. Click on the "Upload Resume" button and select a PDF file
3. Wait for the parsing process to complete
4. View the extracted information displayed on the page

## Development
To set up the development environment:

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Start the development server:
   ```
   python manage.py runserver
   ```

## Testing
Run the test suite with:
```
python manage.py test (yet to be implemented)
```

## Deployment
The project is set up for easy deployment using Docker and GitLab CI/CD. The `.gitlab-ci.yml` file in the repository root defines the CI/CD pipeline. (yet to be implemented)

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
