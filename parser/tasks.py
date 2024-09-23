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

    try:
        """Approach - 1: using 'pyresparser' library - (not able to accurately parse work and education details)"""
        # data: Any = ResumeParser(file_path).get_extracted_data()
        # print(f"extracted data: {data}")

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

        """Approach - 2: custom parsing logic using spaCy (not 100% accurate over various resume formats)"""
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
        # optional - enhances data privacy (delete the file after parsing)
        os.remove(file_path)
