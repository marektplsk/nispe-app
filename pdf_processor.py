import os
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document

def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def process_pdf(file_path):
    # Extract text from the PDF
    pdf_text = extract_text_from_pdf(file_path)
    data = [Document(page_content=pdf_text)]

    # Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=7500, chunk_overlap=100)
    chunks = text_splitter.split_documents(data)

    # Embed the chunks
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="pdf_documents"
    )
    return vector_db

def process_pdfs_from_folder(file_paths, user_question):
    all_context = ""
    for file_path in file_paths:
        print(f"Processing PDF: {file_path}")
        
        # Process the PDF (using your existing process_pdf function)
        vector_db = process_pdf(file_path)
        
        # Retrieve the relevant chunks for the user's question
        retrieved_docs = vector_db.similarity_search(query=user_question, k=3)
        
        # Collect all relevant content into context
        all_context += "\n".join([doc.page_content for doc in retrieved_docs]) + "\n"
    
    return all_context



