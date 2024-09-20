from django.urls import path
from .views import ResumeUploadView, ResumeUploadTemplateView, ResumeDetailView

urlpatterns = [
    path("", ResumeUploadTemplateView.as_view(), name="resume-upload-template"),
    path("upload/", ResumeUploadView.as_view(), name="resume-upload"),
    path("resume/<int:resume_id>/", ResumeDetailView.as_view(), name="resume-detail"),
]
