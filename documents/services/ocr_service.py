import os
from pdf2image import convert_from_path
import numpy as np
from enum import Enum
import cv2
from PIL import Image
import uuid
import shutil
import easyocr
from google.cloud import vision
from io import BytesIO
import os

#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\Caetano\\Downloads\\google_cloud_cred.json"
print("GOOGLE CREDENTIALS:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize EasyOCR reader (use 'en' for English; add more as needed)
reader = easyocr.Reader(['en'], gpu=True)


def pdf_or_image(file_path):
    valid_image_exts = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext in valid_image_exts:
        return "image"
    elif file_ext == '.pdf':
        return "pdf"

    raise ValueError(f"Unsupported file format: '{file_ext}'. Only images and PDFs are allowed.")


from google.cloud import vision
from io import BytesIO

vision_client = vision.ImageAnnotatorClient()


def read_image_with_google_vision(image_input):
    """
    Accepts PIL Image or NumPy array, returns extracted text using Google Vision API.
    """
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



def read_image_with_easyocr(image_input):
    # EasyOCR expects either a file path or a numpy array
    if isinstance(image_input, Image.Image):
        image_input = np.array(image_input.convert("RGB"))

    results = reader.readtext(image_input, detail=0)  # detail=0 returns only the text
    return "\n".join(results)


def read_image(image_path):
    image = Image.open(image_path)
    return image


def read_image_from_pdf(file_path):
    images = convert_from_path(file_path, dpi=300, poppler_path='C:/Users/caetano/Downloads/Release-24.08.0-0/poppler-24.08.0/Library/bin')

    text = ""
    for img in images:
        enchaced_image = enhance_and_threshold(img)
        text += read_image_with_easyocr(enchaced_image) + "\n"

    return text


def enhance_and_threshold(image):
    img = np.array(image.convert("RGB"))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Resize
    scale_factor = 1.5
    img = cv2.resize(img, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)

    # Grayscale + CLAHE for contrast
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Noise reduction
    filtered = cv2.bilateralFilter(gray, 11, 75, 75)

    # Optional: Sharpen
    sharpened = cv2.filter2D(filtered, -1, np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]]))

    # Thresholding
    thresh_adaptive = cv2.adaptiveThreshold(sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 21, 10)
    _, thresh_otsu = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Choose best result
    processed = thresh_adaptive  # or thresh_otsu, depending on your testing

    # Dilation
    kernel = np.ones((2, 2), np.uint8)
    processed = cv2.dilate(processed, kernel, iterations=1)

    return processed


def extract_text_from_upload(upload_file) -> str:
    """
    Save the uploaded file temporarily, run OCR, delete file, return extracted text.
    """
    _, ext = os.path.splitext(upload_file.filename)
    ext = ext.lower()

    if ext not in ('.pdf', '.png', '.jpg', '.jpeg', '.bmp', '.tiff'):
        raise ValueError("Unsupported file type.")

    temp_filename = f"{uuid.uuid4().hex}{ext}"
    temp_path = os.path.join(UPLOAD_DIR, temp_filename)

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    try:
        if pdf_or_image(temp_path) == 'image':
            img = read_image(temp_path)
            img = enhance_and_threshold(img)
            text = read_image_with_easyocr(img)
        else:
            text = read_image_from_pdf(temp_path)
    finally:
        os.remove(temp_path)

    return text.strip()
