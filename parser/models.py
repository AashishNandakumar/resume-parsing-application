from django.db import models


# Create your models here.
class Resume(models.Model):
    file = models.FileField(upload_to="resumes/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    education = models.TextField(blank=True)
    work_experience = models.TextField(blank=True)
    technologies = models.TextField(blank=True)
    college = models.CharField(max_length=255, blank=True)
    designation = models.CharField(max_length=255, blank=True)
    total_experience = models.FloatField(default=0)
    parsed = models.BooleanField(default=False)

    def __str__(self):
        return f"Resume {self.id}"
