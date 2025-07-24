from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from .services import ocr_service, classification_service, entity_extraction_service
from django.shortcuts import render

class DocumentProcessingView(APIView):
    parser_classes = [MultiPartParser]  # To handle file uploads

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Step 1: OCR
            image = ocr_service.read_image(file)
            enhanced = ocr_service.enhance_and_threshold(image)
            text = ocr_service.read_image_with_google_vision(enhanced)

            # Step 2: Classification
            doc_type, confidence = classification_service.classify_document_2(text)

            # Step 3: Entity Extraction
            entities = entity_extraction_service.send_to_llm(doc_type, text)

            return Response({
                "raw_text": text,
                "document_type": doc_type.name,
                "entities": entities,
                "confidence": confidence
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def test_upload_view(request):
    return render(request, "test_upload.html")
