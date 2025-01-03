from flask import render_template, request, redirect, url_for
from . import app
from .pdf_processor import process_pdf, process_pdfs_from_folder
from .models import get_db_connection, fetch_data_from_db
from .mistral_model import get_mistral_response

@app.route('/')
def home():
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    mycursor.execute("SHOW DATABASES")
    databases = mycursor.fetchall()  
    database_exists = False
    for db in databases:
        if db[0] == "nispeDB":
            database_exists = True
            break

    if not database_exists:
        mycursor.execute("CREATE DATABASE nispeDB")
        print("Database 'nispeDB' created successfully!")
    else:
        print("Database 'nispeDB' already exists.")

    mycursor.execute("SHOW DATABASES")
    databases = mycursor.fetchall()

    mycursor.close()
    mydb.close()

    return render_template('index.html', databases=databases)

@app.route('/add', methods=['GET', 'POST'])
def add_data():
    # Add data handling code here
    pass

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if request.method == 'POST':
        user_question = request.form['question']
        uploaded_pdf = request.files.get('pdf')  # Expecting a PDF upload option in the form

        # Initialize variables
        context = ""
        response = ""

        try:
            # Step 1: Determine the query intent
            query_advice = "advice" in user_question.lower()
            query_journal = "journal" in user_question.lower()
            query_pdf = "from pdf" in user_question.lower()
            query_database = "from database" in user_question.lower()
            query_all = "from all" in user_question.lower()

            if query_advice:
                file_paths = [
                    "./uploads/advice/ict-mentor-2022.pdf", 
                    "./uploads/advice/beforefunded-TJR.pdf", 
                    "./uploads/advice/funded-pass-TJR.pdf"
                ]
                context = process_pdfs_from_folder(file_paths, user_question)
            elif query_journal:
                file_paths = [
                    "./uploads/journal/journaling-ict2022.pdf", 
                ]
                context = process_pdfs_from_folder(file_paths, user_question)
            # Handle other queries
            elif query_pdf:
                if uploaded_pdf:
                    file_path = f"./uploads/{uploaded_pdf.filename}"
                    uploaded_pdf.save(file_path)
                    vector_db = process_pdf(file_path)
                else:
                    file_path = "./uploads/advice/ict-mentor-2022.pdf"
                    vector_db = process_pdf(file_path)
                retrieved_docs = vector_db.similarity_search(query=user_question, k=3)
                context = "\n".join([doc.page_content for doc in retrieved_docs])

            elif query_database:
                trades = fetch_data_from_db()
                context = "\n".join([str(trade) for trade in trades])

            elif query_all:
                # Combine advice, journal, and database contexts
                advice_context = process_pdfs_from_folder(["./uploads/advice/ict-mentor-2022.pdf"], user_question)
                journal_context = process_pdfs_from_folder(["./uploads/journal/journaling-ict2022.pdf"], user_question)
                db_context = "\n".join([str(trade) for trade in fetch_data_from_db()])
                context = f"Advice Context:\n{advice_context}\nJournal Context:\n{journal_context}\nDatabase Context:\n{db_context}"

            else:
                response = "Please specify if you want data 'from PDF', 'from database', 'from advice', 'from journal', or 'from all'."

            if context:
                prompt = f"Context:\n{context}\n\nQuestion: {user_question}\nAnswer:"
                response = get_mistral_response(prompt)

        except Exception as e:
            response = f"An error occurred: {e}"

        return render_template('ask.html', question=user_question, response=response)

    return render_template('ask.html')
