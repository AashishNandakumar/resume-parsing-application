import PyPDF2
import spacy
import re


nlp = spacy.load("en_core_web_sm")


def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

    return text


def extract_mail(text):
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9._]+\.[A-Z|a-z]{2,}\b"
    match = re.search(
        email_pattern, text
    )  # search for the first occurence of the pattern
    return (
        match.group() if match else ""
    )  # return the entire matched pattern found in the text


def extract_phone(text):
    phone_pattern = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
    match = re.search(phone_pattern, text)
    return match.group() if match else ""


def extract_name(doc):
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.split("\n")[0]
    return ""


def extract_education(doc):
    education = []
    edu_keywords = ["degree", "bachelor", "master", "phd", "diploma"]
    for sent in doc.sents:
        if any(keyword in sent.text.lower() for keyword in edu_keywords):
            education.append(sent.text.strip())
    return "\n".join(education)


def extract_work_experience(doc):
    experience = []
    # print(f"doc sentences: {doc.sents}")
    work_keywords = [
        "work experience",
        "employment",
        "job",
        "position",
        "intern",
        "developer",
    ]
    for sent in doc.sents:
        # print(f"sentence: {sent}")
        if any(keyword in sent.text.lower() for keyword in work_keywords):
            experience.append(sent.text.strip())
    return "\n".join(experience)


def extract_technologies(doc):
    tech_keywords = set(
        [
            "python",
            "java",
            "javascript",
            "html",
            "c",
            "c++",
            "go",
            "css",
            "django",
            "react",
            "node.js",
            "vue",
            "angular",
            "flask",
            "sql",
            "nosql",
            "aws",
            "docker",
            "kubernetes",
        ]
    )
    technologies = set()
    for token in doc:
        if token.text.lower() in tech_keywords:
            technologies.add(token.text)
    return ", ".join(technologies)


def parse_resume_util(file_path):
    text = extract_text_from_pdf(file_path)
    doc = nlp(text)
    print(doc)

    name = extract_name(doc)
    email = extract_mail(text)
    phone = extract_phone(text)
    education = extract_education(doc)
    work_experience = extract_work_experience(doc)
    technologies = extract_technologies(doc)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "education": education,
        "work_experience": work_experience,
        "technologies": technologies,
    }
