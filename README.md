# 📎 Document Processing System

A Django-based document classification and entity extraction system using OCR, ChromaDB, and optional LLM integration.

---

## 🚀 Features

- Upload and process image/PDF documents
- OCR via EasyOCR (free) or Google Cloud Vision (paid, more accurate)
- Classify documents into 16 types (resume, invoice, letter, etc.)
- Extract relevant entities using a language model
- Store document embeddings and metadata in ChromaDB
- Test and view output via web interface

---

## ⚙️ Installation Options

### ♻️ Option 1: Docker (Recommended)

```bash
# Build the image
docker build -t document-processor .

# Run the container
docker run -p 8000:8000 document-processor
```

Make sure to:

- Place your `credentials.json` in the project root
- Update `.env` with your OpenAI API key

---

### 🛠️ Option 2: Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🔐 Required Setup

### ✅ Add OpenAI API key

Create a `.env` file:

```
OPENAI_API_KEY = "your-gpy-key-here-Bbx_6AregOoXqdYD3caZGAT659WniYArvi5hHpPLcA"
```

### ✅ Set Google Vision credentials

In `services/ocr_service.py`, update:

```python
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\path\\to\\google_cloud_cred.json"
```

---

## 🔍 Choose Your OCR Engine

By default, the project uses **EasyOCR** (fast and free).\
To use **Google Cloud Vision** (slower, more accurate):

1. Replace `read_image_with_easyocr()` in `ocr_service.py` with:

```python
def read_image_with_google_vision(image_input):
    from google.cloud import vision
    from io import BytesIO
    import numpy as np
    from PIL import Image

    vision_client = vision.ImageAnnotatorClient()

    if isinstance(image_input, np.ndarray):
        image_input = Image.fromarray(image_input)

    buffered = BytesIO()
    image_input.save(buffered, format="PNG")
    content = buffered.getvalue()

    image = vision.Image(content=content)
    response = vision_client.document_text_detection(image=image)

    if response.error.message:
        raise Exception(f"Google Vision API error: {response.error.message}")

    return response.full_text_annotation.text
```

2. Re-run the pre-processing to generate new training data.

---

## 🧪 Usage Guide

### ♻️ Process dataset to JSON

Convert raw documents into labeled JSON (used for training):

```bash
python manage.py split_documents
```

---

### 🧠 Train & Upsert into ChromaDB

Process each document, classify it, extract entities, and store in Chroma:

```bash
python manage.py process_documents --input-dir "C:\path\to\documents"
```

---

### 🌐 Web Interface

Run the server:

```bash
python manage.py runserver
```

Then open:\
[http://127.0.0.1:8000/api/test-upload/](http://127.0.0.1:8000/api/test-upload/)

Use this to upload a file and get a structured response.

---

## ⚖️ Core Function Overview

### `ocr_service.py`

- `read_image()` – Load image from disk
- `enhance_and_threshold()` – Preprocess for better OCR accuracy
- `read_image_with_easyocr()` / `read_image_with_google_vision()` – Extract text

---

### `classification_service.py`

- `classify_document_2(text)` → `(DocumentType, confidence)`\
  Classifies text into one of 16 document types

---

### `entity_extraction_service.py`

- `extract(text, document_type)` → `{ field: value }`\
  Extracts structured fields from the text using LLM

---

### `process_documents` command

Batch process and insert documents into ChromaDB:

```bash
python manage.py process_documents --input-dir "/path/to/docs"
```

---

## 📦 ChromaDB

All documents are embedded and stored in a local ChromaDB index at `chroma_data/`.

To clean and reset:

```bash
rm -rf chroma_data/
```

---

## 📄 Supported Document Types

- invoice
- resume
- scientific\_report
- scientific\_publication
- letter
- email
- form
- budget
- memo
- presentation
- advertisement
- questionnaire
- handwritten
- specification
- file\_folder
- news\_article

---

## ✅ Recommendations

- ✅ Use Google Cloud Vision for better accuracy (especially for invoices and forms)
- ✅ Retrain (`split_documents`) if you switch OCR engine
- ✅ Use Docker for reproducible setup

---

## 🤛 Need Help?

If you run into issues or want to extend this with search, table extraction, or LLM comparison — open an issue or message the author.

