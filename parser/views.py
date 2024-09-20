from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ResumeSerializer
from .models import Resume
from django.views.generic import TemplateView
from .tasks import parse_resume
from django.shortcuts import get_object_or_404


# Create your views here.
class ResumeUploadView(APIView):
    def post(self, request, format=None):
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid():
            resume = serializer.save()
            parse_resume.delay(resume.id)  # start asynchronous processing
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResumeDetailView(APIView):
    def get(self, request, resume_id, format=None):
        print("ok", resume_id)
        resume = get_object_or_404(Resume, id=resume_id)
        serializer = ResumeSerializer(resume)  # type conversion
        return Response(serializer.data)


class ResumeUploadTemplateView(TemplateView):
    template_name = "parser/upload.html"
