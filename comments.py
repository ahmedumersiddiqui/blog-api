from flask import Flask, jsonify, request
import psycopg2
import os
from dotenv import load_dotenv
import jwt
import datetime

load_dotenv()

app = Flask(__name__)
db_url = os.getenv("DATABASE_URl")
secret_key = os.getenv("SECRET_KEY")

def is_valid_email(email):
    # Simple email format validation
    return '@' in email

def generate_token(user_id):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    token = jwt.encode({'user_id': user_id, 'exp': expiration}, secret_key, algorithm='HS256')
    return token


@app.route('/api/comments', methods=['POST'])
def add_comment():
    data = request.get_json()
    user_id = data.get('user_id')
    blog_id = data.get('blog_id')
    comment_text = data.get('comment_text')

    if not user_id or not blog_id or not comment_text:
        return jsonify({'error': 'Missing required fields'}), 400

    connection = psycopg2.connect(db_url)
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

        cursor.execute("SELECT * FROM user_blogs WHERE blog_id = %s", (blog_id,))
        blog = cursor.fetchone()

        if not user or not blog:
            return jsonify({'error': 'User or blog not found'}), 404

        cursor.execute("INSERT INTO comments (user_id, blog_id, comment_text) VALUES (%s, %s, %s) RETURNING comment_id",
                       (user_id, blog_id, comment_text))
        comment_id = cursor.fetchone()[0]
        connection.commit()

        return jsonify({'message': 'Comment added successfully', 'comment_id': comment_id}), 201

    except Exception as e:
        connection.rollback()
        return jsonify({'error': f'Error adding comment: {str(e)}'}), 500

    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
