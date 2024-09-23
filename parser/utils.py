import PyPDF2
import spacy
import re
import io
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams

from spacy.matcher.matcher import Matcher
import json


nlp = spacy.load("en_core_web_sm")


def extract_text_from_pdf(pdf_path):
    """Extract text using `PyPDF2`"""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

    return text

    """Extract text using PdfMiner"""
    # output_string = io.StringIO()
    # la_params = LAParams()

    # try:
    #     with open(pdf_path, "rb") as pdf_file:
    #         extract_text_to_fp(
    #             pdf_file,
    #             output_string,
    #             laparams=la_params,
    #             output_type="text",
    #             codec="utf-8",
    #         )

    #         text = output_string.getvalue()

    # except Exception as e:
    #     print(f"Error extracting text from PDF: {e}")
    #     text = ""
    # finally:
    #     output_string.close()

    # return text


def extract_name(doc) -> str:
    """Extracts `name` from resume content."""
    # method-1: Use NER to find PERSON entities
    person_entities = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]

    # method-2: looking for common name patterns
    matcher = Matcher(nlp.vocab)
    patterns = [
        [{"POS": "PROPN"}, {"POS": "PROPN"}],
        [{"POS": "PROPN"}, {"POS": "PROPN"}, {"POS": "PROPN"}],
    ]
    matcher.add("NAME_PATTERNS", patterns)
    matches = matcher(doc)
    potential_names = [doc[start:end] for _, start, end in matches]

    # combine results from both methods
    all_names = person_entities + potential_names

    # filter and clean names
    cleaned_names = []
    for name in all_names:
        # convert to string if necessary
        if isinstance(name, spacy.tokens.span.Span):
            name = name.text
        name = name.strip()
        # remove single-word names (likely to be noise)
        if len(name.split()) > 1:
            # remove names that are too long (likely to be sentences)
            if len(name.split()) <= 3:
                cleaned_names.append(name)

    # if we have multiple name condidates, prefer the one that appears first in the document
    if cleaned_names:
        return min(cleaned_names, key=lambda x: doc.text.index(x))

    return ""


def extract_phone(text) -> str:
    """Extracts `phone-number` from resume content."""
    # define patterns for different phone number formats
    patterns = [
        r"\+?91[-.\s]?\d{10}",  # India: +91 xxxxxxxxxx or other variations
        r"\+?1?\s*\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}",  # US/Cannada: +1 (xxx) xxx-xxxx or other variations
        r"\+?[1-9]\d{1,14}(?:\s*x\d+)?",  # International: Up to 15 digits, optional extension
        r"\d{3}[-.\s]?\d{3}[-.\s]?\d{4}",  # Simple 10-digit: xxx-xxx-xxxx or variations
        r"\(\d{3}\)\s*\d{3}[-.\s]?\d{4}",  # (xxx) xxx-xxxx
        r"\d{10}",  # plain 10 digits
    ]

    # combine all patterns
    combined_pattern = "|".join(patterns)

    # find all matched
    matches = re.findall(combined_pattern, text)

    if matches:
        # print(f"possible matches: {matches}")
        # clean and standardize the first match
        phone = re.sub(r"\D", "", matches[0])  # remove non-digit characters
        # print(f"phone number: {phone}")
        # basic validation (at least 10 digits, not more than 15 digits)
        if 10 <= len(phone) <= 15:
            # format the phone number
            if len(phone) == 10:
                return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
            elif len(phone) == 11 and phone[0] == "1":
                return f"+1 ({phone[1:4]}) {phone[4:7]}-{phone[7:]}"
            elif len(phone) == 12 and phone[:2] == "91":
                return f"(+91) {phone[2:7]}-{phone[7:]}"
            else:
                return f"+{phone}"

    return ""


def extract_mail(text) -> str:
    """Extracts `email-address` from resume content."""
    # regular expression pattern for email addresses
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

    # find all matches
    matches = re.findall(email_pattern, text)

    if matches:
        print(f"possible email matches: {matches}")
        # return the first match (assuming it's the most relevant email)
        return matches[0]

    return ""


def extract_education(text):
    """Extracts `education` from resume content."""
    education_headers = [
        "EDUCATION",
        "ACADEMIC BACKGROUND",
        "ACADEMIC QUALIFICATIONS",
        "EDUCATIONAL QUALIFICATIONS",
    ]

    # find the start of the education section
    education_start = None
    for header in education_headers:
        match = re.search(rf"{header}.*?(?=\n)", text, re.IGNORECASE)
        if match:
            education_start = match.start()
            break

    if not education_start:
        return []

    # find the start of next section if any
    next_section_headers = [
        "EXPERIENCE",
        "WORK EXPERIENCE",
        "EMPLOYMENT",
        "SKILLS",
        "PROJECTS",
        "ACHIVEMENTS",
        "CERTIFICATION",
        "LANGUAGES",
        "INTRESTS",
        "REFERENCES",
    ]

    next_section_start = len(text)
    for header in next_section_headers:
        match = re.search(
            rf"(?<=\n){header}.*?(?=\n)", text[education_start:], re.IGNORECASE
        )
        if match:
            next_section_start = education_start + match.start()
            break

    # extract education information
    education_section = text[education_start:next_section_start].strip()

    education_entries = education_section.split("\n")
    education_data = []
    current_education = {}

    education_matching_pattern = (
        r"(.*?)\s+"
        r"("
        r"(?:\w+\s+)?\d{4}\s*[-–]\s*(?:(?:\w+\s+)?\d{4}|Present|Current)"
        r"|"
        r"\d{4}\s*[-–]\s*\d{4}"
        r"|"
        r"\d{4}\s*[-–]\s*(?:Present|Current)"
        r")"
    )

    for line in education_entries[1:]:  # skip the header
        line = line.strip()
        if not line:
            continue

        degree_match = re.match(education_matching_pattern, line, re.IGNORECASE)
        if degree_match:
            if current_education:
                education_data.append(current_education)
            degree, timeframe = degree_match.groups()
            current_education = {
                "degree": degree.strip(),
                "timeframe": timeframe.strip(),
                "institution": "",
            }
        elif current_education and not current_education.get("institution"):
            current_education["institution"] = line

    if current_education:
        education_data.append(current_education)

    print(f"logging education of the candidate: {education_data}")
    return education_data


def extract_work_experience(text):
    """Extracts `work experience` from resume content."""

    # focus on the Experience section of the resume
    experience_headers = [
        "EXPERIENCE",
        "WORK EXPERIENCE",
        "EMPLOYMENT HISTORY",
        "WORK HISTORY",
        "PROFESSIONAL EXPERIENCE",
        "PROFESSIONAL BACKGROUND",
    ]
    experience_section = None
    for header in experience_headers:
        match = re.search(
            rf"{header}.*(?:EDUCATION|SKILLS|PROJECTS|NOTABLE PROJECTS|NOTABLE PROȷECTS|$)",  # match/obtain all content until the next section is reached
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if match:
            experience_section = match.group(0)
            break
    if not experience_section:
        return []

    experiences = []
    lines = experience_section.split("\n")
    current_role = {}

    for line in lines[1:]:  # skip the header
        line = line.strip()
        if not line:
            continue

        # check for roles by matching - company name followed by date
        role_matching_pattern = (
            r"(.*?)\s+(\w+\s+\d{4}\s*[-–]\s*(?:\w+\s+)?\d{4}|Present)"
        )
        company_date_match = re.match(role_matching_pattern, line)

        if company_date_match:
            if current_role:
                experiences.append(
                    {
                        "organization_name": current_role.get("company", ""),
                        "designation": current_role.get("title", ""),
                        "timeframe": current_role.get("duration", ""),
                    }
                )
            company, duration = company_date_match.groups()
            current_role = {"company": company.strip(), "duration": duration.strip()}
        elif "company" in current_role and not current_role.get("title"):
            current_role["title"] = line
        elif "title" in current_role and not current_role.get("location"):
            current_role["location"] = line

    if current_role:
        experiences.append(
            {
                "organization_name": current_role.get("company", ""),
                "designation": current_role.get("title", ""),
                "timeframe": current_role.get("duration", ""),
            }
        )

    print(f"logging experiences of the candidate: {experiences}")
    return experiences


import re


def extract_skills(text):
    """Extracts `skills` from resume content."""
    skill_headers = [
        "SKILLS",
        "TECHNICAL SKILLS",
        "CORE COMPETENCIES",
        "KEY SKILLS",
        "PROFESSIONAL SKILLS",
        "EXPERTISE",
        "TECHNOLOGIES",
        "TECH STACK",
        "SKILLS SUMMARY",
    ]

    # Find the start of the skills section
    skills_start = None
    for header in skill_headers:
        match = re.search(rf"{header}.*?(?=\n)", text, re.IGNORECASE)
        if match:
            skills_start = match.start()
            break

    if not skills_start:
        return ""

    # Find the start of the next section if any
    next_section_headers = [
        "EXPERIENCE",
        "WORK EXPERIENCE",
        "EMPLOYMENT",
        "EDUCATION",
        "PROJECTS",
        "ACHIEVEMENTS",
        "CERTIFICATIONS",
        "LANGUAGES",
        "INTERESTS",
        "REFERENCES",
    ]

    next_section_start = len(text)
    for header in next_section_headers:
        match = re.search(
            rf"(?<=\n){header}.*?(?=\n)", text[skills_start:], re.IGNORECASE
        )
        if match:
            next_section_start = skills_start + match.start()
            break

    # extract the skills section
    skills_section = text[skills_start:next_section_start].strip()

    skills = set()

    lines = skills_section.split("\n")
    for line in lines[1:]:  # skip the header
        line = line.strip()
        if not line:
            continue

        # remove category labels if any
        line = re.sub(r"\w+\s*:", "", line)

        # remove bullet points and other common list markers
        line = re.sub(r"^[•\-–—*]+", "", line).strip()

        # split by common delimiters
        items = re.split(r"[,|/]", line)
        for item in items:
            skill = item.strip()
            if skill and len(skill) >= 1:
                skills.add(skill)

    # convert set to sorted list and seperate through commas
    skills_list = sorted(list(skills))
    skills_string = ", ".join(skills_list)

    print(f"logging education of the candidate: {skills_string}")
    return skills_string


def parse_resume_util(file_path):
    text = extract_text_from_pdf(file_path)
    print(f"pdf text: {text}")

    doc = nlp(text)
    # print(doc)

    name = extract_name(doc)
    phone = extract_phone(text)
    email = extract_mail(text)
    education = extract_education(text)
    work_experience = extract_work_experience(text)
    technologies = extract_skills(text)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "education": json.dumps(education),
        "work_experience": json.dumps(work_experience),
        "technologies": technologies,
    }
