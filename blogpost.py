from flask import Flask, jsonify, request
import psycopg2
import os
from dotenv import load_dotenv
import jwt
import datetime

load_dotenv()

app = Flask(__name__)
db_url = os.getenv("DATABASE_URl")
secret_key = os.getenv("SECRET_KEY")  # Replace with your secret key

# Function to generate a JWT token
def generate_token(user_id):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    token = jwt.encode({'user_id': user_id, 'exp': expiration}, secret_key, algorithm='HS256')
    return token

@app.route('/api/user_blogs', methods=['POST'])
def create_blog_post():
    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title')
    content = data.get('content')

    if not user_id or not title or not content:
        return jsonify({'error': 'Missing required fields'}), 400

    connection = psycopg2.connect(db_url)
    cursor = connection.cursor()

    try:
        cursor.execute("INSERT INTO user_blogs (user_id, title, content) VALUES (%s, %s, %s) RETURNING blog_id",
                       (user_id, title, content))
        blog_id = cursor.fetchone()[0]
        connection.commit()
        token = generate_token(user_id)

        return jsonify({'message': 'Blog post created successfully', 'blog_id': blog_id, 'token': token}), 201

    except Exception as e:
        connection.rollback()
        return jsonify({'error': f'Error creating blog post: {str(e)}'}), 500

    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
