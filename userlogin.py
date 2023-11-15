from flask import Flask, request
import psycopg2
import os
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
import jwt
import datetime

load_dotenv()

app=Flask(__name__)
db_url=os.getenv("DATABASE_URl")
secret_key=os.getenv("SECRET_KEY")
@app.route('/api/users/login', methods=['POST'])

def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    connection = psycopg2.connect(db_url)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if not user:
        return {'error': 'User not found'}, 404

    if check_password_hash(user[1], password):
        token = jwt.encode({'user_id': user[0], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, secret_key, algorithm='HS256')
        return {'message': 'Login successful', 'token': (token)}, 200
    else:
        return {'error': 'Incorrect password'}, 401

if __name__ == '__main__':
    app.run(debug=True)