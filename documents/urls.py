from django.urls import path
from .views import DocumentProcessingView, test_upload_view

urlpatterns = [
    path("process-document/", DocumentProcessingView.as_view(), name="process_document"),
    path("test-upload/", test_upload_view, name="test_upload"),
]
