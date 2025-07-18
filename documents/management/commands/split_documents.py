from django.core.management.base import BaseCommand
import os
import json
from documents.services import ocr_service  

# Base directories
base_input_dir_train = "C:\\Users\\Caetano\\Desktop\\estudos\\document_classifier\\document_processor\\documents\\data\\processed\\train"
base_input_dir_test = "C:\\Users\\Caetano\\Desktop\\estudos\\document_classifier\\document_processor\\documents\\data\\processed\\test"
base_output_dir_train = "C:\\Users\\Caetano\\Desktop\\estudos\\document_classifier\\document_processor\\documents\\data\\processed\\json_train"
base_output_dir_test = "C:\\Users\\Caetano\\Desktop\\estudos\\document_classifier\\document_processor\\documents\\data\\processed\\json_test"

folders = [
    'advertisement', 'budget', 'email', 'file_folder', 'form', 'handwritten',
    'invoice', 'letter', 'memo', 'news_article', 'presentation', 'questionnaire',
    'resume', 'scientific_publication', 'scientific_report', 'specification'
]

class Command(BaseCommand):
    help = 'Classify and split documents into JSON'

    def handle(self, *args, **kwargs):
        os.makedirs(base_output_dir_train, exist_ok=True)
        os.makedirs(base_output_dir_test, exist_ok=True)

        def process_split(input_dir, output_dir, split_name):
            for label in folders:
                folder_path = os.path.join(input_dir, label)
                if not os.path.isdir(folder_path):
                    continue

                samples = []

                for root, dirs, files in os.walk(folder_path):
                    for filename in files:
                        file_path = os.path.join(root, filename)
                        try:
                            img = ocr_service.read_image(file_path)
                            img = ocr_service.enhance_and_threshold(img)
                            text = ocr_service.read_image_with_easyocr(img).replace('\n', '\\n')
                            samples.append({"text": text, "label": label})
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"Error processing {file_path}: {e}"))

                output_file = os.path.join(output_dir, f"samples_{label}.json")
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(samples, f, indent=2, ensure_ascii=False)
                self.stdout.write(self.style.SUCCESS(f"Saved {len(samples)} samples to {output_file}"))

        process_split(base_input_dir_train, base_output_dir_train, "train")
        process_split(base_input_dir_test, base_output_dir_test, "test")
