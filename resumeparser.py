import os
import yaml
from dotenv import load_dotenv
import google.generativeai as genai
import json
import re

# Load environment variables
load_dotenv()

# Load API keys
CONFIG_PATH = "config.yaml"
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key and os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as file:
        data = yaml.safe_load(file)
        gemini_api_key = data.get("GEMINI_API_KEY")

genai.configure(api_key=gemini_api_key)

def is_gemini_available():
    if not gemini_api_key:
        print("❌ Gemini API key is missing.")
        return False
    try:
        models = list(genai.list_models())
        if not models:
            print("❌ No models available.")
            return False
        print("✅ Gemini API is available. Available models:", [m.name for m in models])
        return True
    except Exception as e:
        print(f"⚠️ Gemini API unavailable: {e}")
        return False

def select_gemini_model():
    if is_gemini_available():
        print("🚀 Selecting Gemini model for resume parsing...")
        models = list(genai.list_models())
        preferred_models = ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]
        for model in models:
            if "generateContent" in model.supported_generation_methods and model.name in preferred_models:
                print(f"Selected model: {model.name}")
                return model.name
        for model in models:
            if "generateContent" in model.supported_generation_methods:
                print(f"Selected fallback model: {model.name}")
                return model.name
        raise ValueError("❌ No suitable Gemini model found for generateContent.")
    else:
        raise ValueError("❌ No available Gemini API. Check your API key or availability.")

def ats_extractor(resume_data):
    model_name = select_gemini_model()
    prompt = """
    You are an AI bot designed to extract and optimize resume details for ATS compatibility.
    Extract the following information from the provided resume and format it for ATS approval, ensuring keyword-rich, concise, and structured content:
    - Full Name
    - Email
    - Phone (if available)
    - GitHub Profile (if available)
    - LinkedIn Profile (if available)
    - Employment History (as a list of objects with Job Title, Company, Dates, Description, emphasizing measurable achievements and technical skills)
    - Technical Skills (as a list, including relevant tools, software, and technologies)
    - Soft Skills (as a list)
    - Education (as a list of objects with Degree, Institution, Location, Dates, and relevant honors or achievements)
    - Certifications (as a list, including title and date if available)
    - Awards (as a list, including title and date if available)
    Return the result as a valid JSON string, enclosed in curly braces `{}`. If a field is missing, use an empty string `""` or an empty array `[]` as appropriate. Ensure the entire response is pure JSON with no additional text, comments, or Markdown markers (e.g., ```json).
    Resume data:
    """
    try:
        model_instance = genai.GenerativeModel(model_name)
        response = model_instance.generate_content(prompt + resume_data)
        if response and response.text:
            raw_response = response.text.strip()
            print("Raw response from Gemini API:", repr(raw_response))
            cleaned_response = re.sub(r'^```json\s*|\s*```$', '', raw_response, flags=re.MULTILINE).strip()
            print("Cleaned response:", repr(cleaned_response))
            try:
                parsed_data = json.loads(cleaned_response)
                if isinstance(parsed_data, dict):
                    print("Successfully parsed JSON:", parsed_data)
                    return parsed_data
                else:
                    print("⚠️ Parsed response is not a dictionary:", parsed_data)
                    return {"error": "Response is not a JSON object", "raw_response": raw_response}
            except json.JSONDecodeError as e:
                print(f"⚠️ Failed to parse JSON: {e}. Cleaned response:", cleaned_response)
                return {"error": "Invalid JSON format", "raw_response": raw_response}
        else:
            print("⚠️ Empty response from Gemini API.")
            return {"error": "Empty response from Gemini API"}
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return {"error": str(e)}