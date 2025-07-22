import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from enum import Enum
import os
import json
import re
import pickle
from typing import Tuple, Optional
from django.conf import settings  


class DocumentType(Enum):
    specification = 1
    email = 2
    advertisement = 3
    handwritten = 4
    scientific_report = 5
    budget = 6
    scientific_publication = 7
    presentation = 8
    file_folder = 9
    memo = 10
    resume = 11
    invoice = 12
    letter = 13
    questionnaire = 14
    form = 15
    news_article = 16

json_folder = os.path.join(settings.BASE_DIR, "documents", "data", "processed", "json_train")
index_path = "doc_index.faiss"
labels_path = "doc_labels.pkl"
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def load_documents(json_folder: str):
    doc_texts, doc_labels = [], []
    file_paths = [os.path.join(json_folder, f) for f in os.listdir(json_folder)]
    
    for path in file_paths:
        with open(path, "r", encoding="utf-8") as f:
            try:
                data_list = json.load(f)
            except json.JSONDecodeError:
                print(f"Invalid JSON in file: {path}")
                continue

            for item in data_list:
                doc_type_str = item.get("label")
                text = item.get("text")
                if not doc_type_str or not text:
                    continue

                try:
                    doc_type = DocumentType[doc_type_str]
                except KeyError:
                    print(f"Unknown document type '{doc_type_str}' in {path}")
                    continue

                doc_texts.append(text)
                doc_labels.append(doc_type.value)

    return doc_texts, doc_labels


# Load or Compute Embeddings
# -------------------------
if os.path.exists(index_path) and os.path.exists(labels_path):
    print("Loading FAISS index and labels from disk...")
    index = faiss.read_index(index_path)
    with open(labels_path, "rb") as f:
        doc_labels = pickle.load(f)
else:
    print("Generating embeddings and indexing...")
    doc_texts, doc_labels = load_documents(json_folder)
    embeddings = embedding_model.encode(doc_texts, convert_to_numpy=True)
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save
    faiss.write_index(index, index_path)
    with open(labels_path, "wb") as f:
        pickle.dump(doc_labels, f)



# Document Classification
# -------------------------
def softmax(x):
    e_x = np.exp(-x)  # negative distances = higher score
    return e_x / e_x.sum()


def classify_document(text: str, threshold: float = 0.3) -> Tuple[Optional[DocumentType], float]:
    query_vec = embedding_model.encode([(text)], convert_to_numpy=True)
    D, I = index.search(query_vec, k=3)  # use top-3 for softmax confidence

    scores = softmax(D[0])
    best_score = scores[0]
    best_index = I[0][0]

    if best_score < threshold:
        return None, best_score

    class_value = doc_labels[best_index]
    predicted_class = DocumentType(class_value)

    best_score = float(best_score)
    return predicted_class, best_score


def classify_document_2(text: str) -> tuple[DocumentType, float]:
    query_vec = embedding_model.encode([text])
    D, I = index.search(query_vec, k=3)
    closest_index = I[0][0]
    distance = D[0][0]

    confidence = 1 / (1 + distance)  # Just a normalized score, can be improved

    class_value = doc_labels[closest_index]
    predicted_class = DocumentType(class_value)

    return predicted_class, confidence


