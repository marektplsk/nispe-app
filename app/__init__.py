from flask import Flask
from langchain_ollama import OllamaLLM
from .pdf_processor import process_pdf, process_pdfs_from_folder

app = Flask(__name__)

# Initialize the Mistral model
mistral_model = OllamaLLM(model="mistral")

# Add other configurations here
app.config['TEMPLATES_AUTO_RELOAD'] = True

