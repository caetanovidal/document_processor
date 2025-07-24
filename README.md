# 📎 Document Processing System

A Django-based document classification and entity extraction system using OCR, ChromaDB, and optional LLM integration.

---

## 🚀 Features

- Upload and process image/PDF documents
- OCR via **Google Cloud Vision** (default) or EasyOCR (optional)
- Classify documents into 16 types (resume, invoice, letter, etc.)
- Extract relevant entities using a language model
- Store document embeddings and metadata in **ChromaDB**
- Web UI to test and view output

---

## ⚙️ Installation Options

### ♻️ Option 1: Docker (Recommended)

#### ✅ Build the image

```bash
docker build -t document-processor .
```

#### ✅ Run the container (with Google Vision enabled)

```cmd
docker run -p 8000:8000 ^
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json ^
  -v %cd%:/app ^
  document-processor
```

#### 🔎 Docker usage examples

**Process and index documents in ChromaDB:**

```cmd
docker run --rm -v %cd%:/app document-processor ^
  python manage.py process_documents --input-dir "/app/processed_documents/test/email"
```

**Preprocess dataset and split into JSON samples:**

```cmd
docker run --rm -v %cd%:/app document-processor ^
  python manage.py split_documents
```

**Run Django server:**

```cmd
docker run -p 8000:8000 -v %cd%:/app document-processor ^
  python manage.py runserver 0.0.0.0:8000
```

---

### 🛠️ Option 2: Manual Setup

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

---

## 🔐 Required Setup

### ✅ Add OpenAI API Key

Create a `.env` file:

```dotenv
OPENAI_API_KEY=your-openai-key-here
```

### ✅ Add Google Vision Credentials

Place your `credentials.json` in the root of the project. Docker uses:

```
/app/credentials.json
```

You don’t need to manually set `os.environ[...]` inside the code. Docker handles it.

---

## 🔍 OCR Engine Configuration

Google Cloud Vision is now the **default OCR engine**.

If you want to switch to EasyOCR (free & fast):

- Modify `ocr_service.py` to use `read_image_with_easyocr()`
- Re-run:

```bash
python manage.py split_documents
```

---

## 🧪 Usage Guide

### ♻️ Preprocess to JSON

```bash
python manage.py split_documents
```

Or in Docker:

```bash
docker run --rm -v %cd%:/app document-processor ^
  python manage.py split_documents
```

### 🧠 Process & Insert into ChromaDB

```bash
python manage.py process_documents --input-dir "C:\\path\\to\\documents"
```

Or in Docker:

```bash
docker run --rm -v %cd%:/app document-processor ^
  python manage.py process_documents --input-dir "/app/processed_documents/test/email"
```

### 🌐 Launch Web Interface

```bash
python manage.py runserver
```

Or in Docker:

```bash
docker run -p 8000:8000 -v %cd%:/app document-processor ^
  python manage.py runserver 0.0.0.0:8000
```

Then open:

```
http://127.0.0.1:8000/api/test-upload/
```

---

## ⚖️ Core Function Overview

### `ocr_service.py`

- `read_image()` — Load image from disk
- `enhance_and_threshold()` — Preprocess for better OCR
- `read_image_with_google_vision()` — Google OCR (default)
- `read_image_with_easyocr()` — Optional OCR engine

### `classification_service.py`

- `classify_document_2(text) → (DocumentType, confidence)`

### `entity_extraction_service.py`

- `extract(text, document_type) → { field: value }`

### `process_documents` command

```bash
python manage.py process_documents --input-dir "/path/to/docs"
```

---

## 📆 ChromaDB

Documents are embedded and stored in:

```
chroma_data/
```

To reset:

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

- Use **Google Cloud Vision** for better OCR accuracy (default)
- Re-run `split_documents` if you switch OCR engine
- Use Docker for consistency across environments

---

## 🤛 Need Help?

For bugs, feature requests, or support, open an issue or contact the author.

