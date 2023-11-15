from flask import Flask, jsonify, request
import psycopg2
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import jwt
import datetime

load_dotenv()

app = Flask(__name__)
db_url = os.getenv("DATABASE_URl")
secret_key = os.getenv("SECRET_KEY") 

@app.route('/api/users/register', methods=['POST'])
def register_user():
    data = request.get_json()
    email = data.get('email')
    password = generate_password_hash(data.get('password'))

    if not email or not password:
        return jsonify({'error': 'Missing email, password'}), 400
    
    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    connection = psycopg2.connect(db_url)
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 400

        cursor.execute("INSERT INTO users (email, pwd) VALUES (%s, %s) RETURNING user_id", (email, password))
        user_id = cursor.fetchone()[0]
        connection.commit()

        token = generate_token(user_id)

        return jsonify({'message': 'User registered successfully', 'token': token}), 201

    except Exception as e:
        connection.rollback()
        return jsonify({'error': f'Error registering user: {str(e)}'}), 500

    finally:
        cursor.close()
        connection.close()

def is_valid_email(email):
    return '@' in email

def generate_token(user_id):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    token = jwt.encode({'user_id': user_id, 'exp': expiration}, secret_key, algorithm='HS256')
    return token

if __name__ == '__main__':
    app.run(debug=True)
