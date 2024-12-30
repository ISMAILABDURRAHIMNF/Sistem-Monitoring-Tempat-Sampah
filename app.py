from flask import Flask, request, jsonify
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv('HOSTNAME'),
        user=os.getenv('USERNAME'),
        password=os.getenv('PASSWORD'), 
        database=os.getenv('DATABASE')
    )
    return conn

@app.route('/', methods=['GET'])
def data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query_ultrasonik = "SELECT * FROM ultrasonik"
        cursor.execute(query_ultrasonik)
        ultrasonik_data = cursor.fetchall()

        query_kelembapan = "SELECT * FROM kelembapan"
        cursor.execute(query_kelembapan)
        kelembapan_data = cursor.fetchall()
        
        result = {
            "ultrasonik": ultrasonik_data,
            "kelembapan": kelembapan_data
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/input', methods=['POST'])
def save_sensor_data():
    data = request.get_json()
    jarak = data.get('jarak')
    kelembapan = data.get('kelembapan')

    if jarak is None or kelembapan is None:
        return jsonify({"error": "Jarak dan/atau kelembapan tidak ditemukan"}), 400

    presentase_ultrasonik = 100 - (jarak - 10)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert data ultrasonik
        query_ultrasonik = "INSERT INTO ultrasonik (timestamp, jarak, presentase) VALUES (NOW(), %s, %s)"
        cursor.execute(query_ultrasonik, (jarak, presentase_ultrasonik))

        # Insert data kelembapan
        query_kelembapan = "INSERT INTO kelembapan (timestamp, presentase_kelembapan) VALUES (NOW(), %s)"
        cursor.execute(query_kelembapan, (kelembapan,))

        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "message": "Data berhasil disimpan",
        "ultrasonik_presentase": presentase_ultrasonik,
        "kelembapan_presentase": kelembapan
    }), 201

if __name__ == '__main__':
    app.run(debug=True)
