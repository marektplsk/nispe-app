import mysql.connector
from flask import Flask, render_template, request, redirect, url_for
from langchain_ollama import OllamaLLM
from pdf_processor import process_pdf
from pdf_processor import process_pdfs_from_folder





app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True

mistral_model = OllamaLLM(model="mistral")




def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="marek123",
        database="nispeDB"  
    )

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
    if request.method == 'POST':
        print("Received Form Data:", dict(request.form))

        try:
            name = request.form.get('name')
            pair = request.form.get('pair')
            _isWin = request.form.get('_isWin')
            risk = request.form.get('risk')
            risk_reward = request.form.get('risk_reward')
            trading_session = request.form.get('trading_session')
            description = request.form.get('description')
            _tradeType = request.form.get('_tradeType')

            selected_tags = request.form.getlist('tags')  

            tags_string = ', '.join(selected_tags) if selected_tags else '' 

            required_fields = ['name', 'pair', '_isWin', 'risk', 'risk_reward', 'trading_session', 'description', '_tradeType']
            missing_fields = [field for field in required_fields if not request.form.get(field)]

            if missing_fields:
                return f"Missing required fields: {', '.join(missing_fields)}"

            mydb = get_db_connection()
            mycursor = mydb.cursor()

            sql_query = """
            INSERT INTO trades 
            (name, pair, _isWin, risk, risk_reward, trading_session, description, _tradeType, tags, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            values = (name, pair, _isWin, risk, risk_reward, trading_session, description, _tradeType, tags_string)

            print(f"Executing SQL Query: {sql_query}")
            print(f"With Values: {values}")

            mycursor.execute(sql_query, values)
            mydb.commit()

            mycursor.close()
            mydb.close()

            return redirect(url_for('view_data'))

        except Exception as e:
            print(f"Error occurred: {e}")
            return "An error occurred while adding the trade."

    return render_template('add.html')

@app.route('/view')
def view_data():
    try:
        mydb = get_db_connection()
        mycursor = mydb.cursor()

        mycursor.execute("SELECT name, pair, _isWin, risk, risk_reward, trading_session, description, _tradeType, tags FROM trades")
        trades = mycursor.fetchall()

        print("Fetched Trades:", trades)

        mycursor.close()
        mydb.close()

        return render_template('view.html', trades=trades)

    except Exception as e:
        print(f"Error occurred: {e}")
        return "An error occurred while fetching the trades."


from pdf_processor import process_pdf  


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
            query_advice = "advice" in user_question.lower()  # Query for advice PDFs
            query_journal = "journal" in user_question.lower()  # Query for journal PDFs
            query_pdf = "from pdf" in user_question.lower()  # Query for uploaded PDFs
            query_database = "from database" in user_question.lower()  # Query for database
            query_all = "from all" in user_question.lower()  # Query to gather everything (advice, journal, and database)

            if query_advice:
                file_paths = [
                    "./uploads/advice/ict-mentor-2022.pdf", 
                    "./uploads/journal/funedjourney-TJR.pdf", 
                    "./uploads/advice/beforefunded-TJR.pdf" 
                ]
                context = process_pdfs_from_folder(file_paths, user_question)

            elif query_journal:
                file_paths = [
                    "./uploads/journal/journaling-ict2022.pdf", 
                    "./uploads/journal/funedjourney-TJR.pdf" , 
                    "./uploads/advice/funded-pass-TJR.pdf"  
                ]
                context = process_pdfs_from_folder(file_paths, user_question)

            # Step 4: Handle PDF-specific queries (uploaded or default)
            elif query_pdf:
                if uploaded_pdf:
                    # Save the uploaded PDF file
                    file_path = f"./uploads/{uploaded_pdf.filename}"
                    uploaded_pdf.save(file_path)
                    print(f"PDF saved at: {file_path}")

                    # Process the uploaded PDF
                    vector_db = process_pdf(file_path)
                else:
                    # Default to a pre-defined PDF (you could add logic here to specify if it's advice or journal)
                    file_path = "./uploads/advice/ict-mentor-2022.pdf"
                    print(f"Using default PDF: {file_path}")

                    # Process the default PDF
                    vector_db = process_pdf(file_path)

                # Retrieve the most relevant chunks for the user's question
                retrieved_docs = vector_db.similarity_search(query=user_question, k=3)
                context = "\n".join([doc.page_content for doc in retrieved_docs])

            # Step 5: Handle database-specific queries
            elif query_database:
                mydb = get_db_connection()
                mycursor = mydb.cursor()

                # Fetch data from the database
                mycursor.execute(
                    "SELECT name, pair, _isWin, risk, risk_reward, trading_session, description, _tradeType, tags FROM trades"
                )
                trades = mycursor.fetchall()

                # Combine trade data into context
                context = "\n".join([
                    f"Name: {trade[0]}, Pair: {trade[1]}, _isWin: {trade[2]}, Risk: {trade[3]}, Risk Reward: {trade[4]}, "
                    f"Trading Session: {trade[5]}, Description: {trade[6]}, Trade Type: {trade[7]}, Tags: {trade[8]}"
                    for trade in trades
                ])

                mycursor.close()
                mydb.close()

            elif query_all:
                advice_file_paths = [
                    "./uploads/advice/ict-mentor-2022.pdf", 
                    "./uploads/advice/beforefunded-TJR.pdf", 
                    "./uploads/advice/funded-pass-TJR.pdf"
                ]
                journal_file_paths = [
                    "./uploads/journal/journaling-ict2022.pdf", 
                    "./uploads/journal/funedjourney-TJR.pdf"
                ]

                all_file_paths = advice_file_paths + journal_file_paths

                advice_context = process_pdfs_from_folder(all_file_paths, user_question)


                context = f"Advice Context:\n{advice_context}\n\nJournal Context:\n{journal_context}"

                mydb = get_db_connection()
                mycursor = mydb.cursor()

                mycursor.execute("SELECT name, pair, _isWin, risk, risk_reward, trading_session, description, _tradeType, tags FROM trades")
                trades = mycursor.fetchall()

                db_context = "\n".join([
                    f"Name: {trade[0]}, Pair: {trade[1]}, _isWin: {trade[2]}, Risk: {trade[3]}, Risk Reward: {trade[4]}, "
                    f"Trading Session: {trade[5]}, Description: {trade[6]}, Trade Type: {trade[7]}, Tags: {trade[8]}"
                    for trade in trades
                ])

                mycursor.close()
                mydb.close()

               


                # Add database context to the final context
                context += f"\n\nDatabase Context:\n{db_context}"

            # Step 7: If no specific query type matched, prompt the user
            else:
                response = "Please specify if you want data 'from PDF', 'from database', 'from advice', 'from journal', or 'from all'."

            # Step 8: Generate a response if context is ready
            if context:
                # Format the model's input prompt
                prompt = f"Context:\n{context}\n\nQuestion: {user_question}\nAnswer:"
                print("\nPrompt Sent to Model:")
                print(prompt)

                # Call the model to generate a response
                response = mistral_model(prompt)

        except Exception as e:
            response = f"An error occurred: {e}"

        return render_template('ask.html', question=user_question, response=response)

    return render_template('ask.html')





def fetch_data_from_db():
    try:
        mydb = get_db_connection()
        mycursor = mydb.cursor()
        mycursor.execute("SELECT name, pair, _isWin, risk, risk_reward, trading_session, description, _tradeType, tags FROM trades")
        trades = mycursor.fetchall()
        mycursor.close()
        mydb.close()
        return trades
    except Exception as e:
        print(f"Error fetching data from DB: {e}")
        return []

def generate_prompt():
    trades = fetch_data_from_db()
    if not trades:
        return "No trade data available."
    prompt = "Here are the latest trades:\n"
    for trade in trades:
        prompt += f"Name: {trade[0]}, Pair: {trade[1]}\n"
    return prompt

def get_mistral_response():
    prompt = generate_prompt()
    try:
        response = mistral_model(prompt)
        return response
    except Exception as e:
        print(f"Error in get_mistral_response: {e}")
        return "An error occurred while processing your request."
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)


