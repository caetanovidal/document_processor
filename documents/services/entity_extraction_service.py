import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def field_list_factory(document_type):
    if document_type.value == 1:
        return ["brand name", "product"]
    elif document_type.value == 2:
        return ["name", "subject", "receiver"]
    elif document_type.value == 3:
        return ["brand name"]
    elif document_type.value == 4:
        return ["subject"]
    elif document_type.value == 5:
        return ["topic", "year"]
    elif document_type.value == 6:
        return ["total amount", "company"]
    elif document_type.value == 7:
        return ["topic", "key words"]
    elif document_type.value == 8:
        return ["author name", "place", "year"]
    elif document_type.value == 9:
        return ["folder name"]
    elif document_type.value == 10:
        return ["date", "from", "subject"]
    elif document_type.value == 11:
        return ["name", "years of experience", "area"]
    elif document_type.value == 12:
        return ["amount", "company", "description"]
    elif document_type.value == 13:
        return ["date", "author", "recipient", "subject"]
    elif document_type.value == 14:
        return ["total number questions", "subject"]
    elif document_type.value == 15:
        return ["subject"]
    elif document_type.value == 16:
        return ["topic", "key words"]
    return []



def send_to_llm(document_type, document_text):
    field_list = field_list_factory(document_type)

    prompt = f"""
You are an information extraction assistant.

Given the following OCR-extracted text from a document of type '{document_type.name}', extract the following fields:
{', '.join(field_list)}

Return only a valid JSON object. Do not include explanations or additional text.

Document Text:
\"\"\"
{document_text}
\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        raw_response = response.choices[0].message.content

        # Validate and parse JSON
        entities = json.loads(raw_response)

        # Optionally ensure all expected fields are in the response
        missing = [f for f in field_list if f not in entities]
        for m in missing:
            entities[m] = None  # Fill missing fields with None

        return entities

    except json.JSONDecodeError:
        print("⚠️ LLM response was not valid JSON:\n", raw_response)
        return {}
    except Exception as e:
        print("❌ Error calling LLM:", e)
        return {}

    