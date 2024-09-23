"""
Celery:
We will use celery to handle the résumé parsing as an asynchronous task.
This will prevent long-running parsing operations from blocking the main app thread and
    improve responsiveness.
"""

import os
from celery import shared_task
from pandas.core.arrays.arrow.array import Any
from pyresparser import ResumeParser
from .utils import parse_resume_util
from .models import Resume
from django.shortcuts import get_object_or_404
import re
from datetime import datetime


@shared_task
def parse_resume(resume_id):
    resume: Resume = get_object_or_404(Resume, id=resume_id)
    file_path = resume.file.path
    # print(f"File path: {file_path}")
    try:
        # parsing using 'pyresparser' library
        # data: Any = ResumeParser(file_path).get_extracted_data()
        # print(f"extracted data: {data}")

        # Approach - 1 (not able to accurately parse work and education details)
        # resume.name = data.get("name", "") if data.get("name") else ""
        # resume.email = data.get("email", "") if data.get("email") else ""
        # resume.phone_number = (
        #     data.get("mobile_number", "") if data.get("mobile_number") else ""
        # )
        # resume.technologies = (
        #     ", ".join(data.get("skills", [])) if data.get("skills") else ""
        # )
        # resume.education = data.get("degree", [""])[0] if data.get("degree") else ""
        # work_experience = data.get("experience", []) if data.get("experience") else ""
        # if work_experience:
        #     # pick the first item i.e, the most recent job
        #     recent_job = " ".join(work_experience[:2])  # combine company name and position
        #     resume.work_experience = recent_job
        # else:
        #     resume.work_experience = ""
        # resume.college = data.get("college_name", "") if data.get("college_name") else ""
        # resume.designation = (
        #     data.get("designation", [""])[0] if data.get("designation") else ""
        # )
        # resume.total_experience = (
        #     data.get("total_experience", 0) if data.get("total_experience") else 0
        # )
        # resume.parsed = True
        # resume.save()

        # Approach - 2
        # resume.name = data.get("name", "")
        # resume.email = data.get("email", "")
        # resume.phone_number = data.get("mobile_number", "")
        # resume.technologies = ", ".join(data.get("skills", []))

        # TODO: enhanced education parsing
        # education = data.get("degree", [])
        # education_info = []
        # pattern = r"(.+?)\s*(\d{4}\s*-\s*\d{4}|\d{4})"
        # for edu in education:
        #     # pattern we are looking for: institution name and timeframe
        #     match = re.search(pattern, edu)
        #     if match:
        #         institution = match.group(1).strip()
        #         timeframe = match.group(2)
        #         education_info.append(f"{institution} ({timeframe})")
        # if education_info:
        #     resume.education = "\n".join(education_info)
        # else:
        #     resume.education = "\n".join(education)

        # # TODO: enhanced work experience parsing
        # experience = data.get("experience", [])
        # work_info = []
        # current_company = ""
        # current_position = ""
        # current_duration = ""
        # pattern1 = r"^([A-Z][a-z0-9]+|[A-Z]+)(\s+([A-Z][a-z0-9]+|[A-Z]+))*$"
        # pattern2 = r"\d{4}\s*-\s*(\d{4}|Present)"
        # for exp in experience:
        #     if re.match(pattern1, exp):  # matches companies
        #         if current_company:
        #             work_info.append(
        #                 f"{current_company}: {current_position} {current_duration}"
        #             )
        #         current_company = exp
        #         current_position = ""
        #         current_duration = ""
        #     elif re.search(pattern2, exp):  # matches durations
        #         current_duration = exp
        #     elif current_company and not current_position:  # matches position
        #         current_position = exp

        # if current_company:
        #     work_info.append(
        #         f"{current_company}: {current_position} {current_duration}"
        #     )
        # print(f"work experience: {work_info}")
        # resume.work_experience = "\n".join(work_info)

        # resume.college = (
        #     data.get("college_name", "") if data.get("college_name") else ""
        # )
        # resume.designation = (
        #     data.get("designation", [""])[0] if data.get("designation") else ""
        # )
        # resume.total_experience = data.get("total_experience", 0)
        # resume.parsed = True
        # resume.save()

        # Custom parsing logic using spaCy (not accurate over various resume formats)
        data = parse_resume_util(file_path)

        resume.name = data.get("name")
        resume.email = data.get("email")
        resume.phone_number = data.get("phone")
        resume.education = data.get("education")
        resume.work_experience = data.get("work_experience")
        resume.technologies = data.get("technologies")
        resume.parsed = True
        resume.save()
        print(f"Resume {resume_id} successfully parsed and saved")
    except Exception as e:
        print(f"Error parsing resume {resume_id}: {str(e)}")
        resume.parsed = False
        resume.save()
    finally:
        # optional - enhances data privacy
        os.remove(file_path)
