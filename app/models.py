import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="marek123",
        database="nispeDB"
    )

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
