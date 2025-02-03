import mysql.connector
from flask import Flask, render_template, request, redirect, url_for
from pdf_processor import process_pdf
from pdf_processor import process_pdfs_from_folder
from deepseek_model import get_deepseek_response 
import time

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

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

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if request.method == 'POST':
        user_question = request.form['question']
        response = ""

        try:
            print(f"\n📝 User Question: {user_question}")  # Log input

            # Step 1: Fetch Data from Database
            print("📡 Fetching data from the database...")
            mydb = get_db_connection()
            mycursor = mydb.cursor()

            mycursor.execute(
                "SELECT name, pair, _isWin, risk, risk_reward, trading_session, description, _tradeType, tags FROM trades"
            )
            trades = mycursor.fetchall()

            if not trades:
                response = "No relevant data found in the database."
                print(response)
                return render_template('ask.html', question=user_question, response=response)

            # Step 2: Format Data for Model
            print("🔍 Formatting database results for AI model...")
            context = "\n".join([
                f"Name: {trade[0]}, Pair: {trade[1]}, _isWin: {trade[2]}, Risk: {trade[3]}, Risk Reward: {trade[4]}, "
                f"Trading Session: {trade[5]}, Description: {trade[6]}, Trade Type: {trade[7]}, Tags: {trade[8]}"
                for trade in trades
            ])

            mycursor.close()
            mydb.close()
            print("✅ Database context retrieved.")

            # Step 3: Send to AI Model with Reasoning Logging
            prompt = f"Database Context:\n{context}\n\nQuestion: {user_question}\nAnswer:"
            print("\n🚀 Sending Prompt to AI Model:")
            print(prompt)

            print("\n🤖 AI is thinking...\n")

            # Get response with real-time streaming
            response = get_deepseek_response(prompt)

        except Exception as e:
            response = f"❌ An error occurred: {e}"
            print(response)

        return render_template('ask.html', question=user_question, response=response)

    return render_template('ask.html')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)