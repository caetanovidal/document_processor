import chromadb
from chromadb.config import Settings
import os
from django.conf import settings

# Set ChromaDB path inside project root
CHROMA_PATH = os.path.join(settings.BASE_DIR, "chroma_data")

client = chromadb.Client(Settings(
    persist_directory=CHROMA_PATH,
    anonymized_telemetry=False
))

def get_chroma_collection(collection_name="documents"):
    return client.get_or_create_collection(name=collection_name)
