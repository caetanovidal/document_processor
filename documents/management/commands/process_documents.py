from django.core.management.base import BaseCommand
import os
import json
import traceback
from documents.services import ocr_service, classification_service, entity_extraction_service
from documents.utils.chromadb_utils import get_chroma_collection
from django.conf import settings
from tqdm import tqdm

class Command(BaseCommand):
    help = 'Processes a dataset, classifies documents, extracts entities, and upserts into ChromaDB.'

    def add_arguments(self, parser):
        parser.add_argument('--input-dir', type=str, required=True, help='Path to input folder containing documents')

    def handle(self, *args, **options):
        input_dir = options['input_dir']
        collection = get_chroma_collection("documents") 

        for root, dirs, files in os.walk(input_dir):
            for filename in tqdm(files):
                if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')):
                    continue

                file_path = os.path.join(root, filename)

                try:
                    # OCR
                    img = ocr_service.read_image(file_path)
                    enhanced = ocr_service.enhance_and_threshold(img)
                    text = ocr_service.read_image_with_easyocr(enhanced)

                    # Classification
                    doc_type, confidence = classification_service.classify_document_2(text)
                    confidence = float(confidence)

                    # Entity Extraction
                    entities = entity_extraction_service.send_to_llm(doc_type, text)
                    flat_entities = {
                        f"entity_{key}": (
                            ", ".join(value) if isinstance(value, list)
                            else str(value) if not isinstance(value, (str, int, float, bool)) and value is not None
                            else value
                        )
                        for key, value in entities.items()
                    }

                    # Upsert to ChromaDB
                    metadata = {
                        "filename": filename,
                        "type": doc_type.name,
                        **flat_entities,
                        "confidence": confidence
                    }
                    collection.upsert(
                        documents=[text],
                        ids=[filename],
                        metadatas=[metadata]
                    )

                    self.stdout.write(self.style.SUCCESS(f"✔ Processed {filename} as {doc_type.name}"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Failed to process {filename}: {e}"))
                    traceback.print_exc()
