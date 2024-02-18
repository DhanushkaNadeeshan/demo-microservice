from flask import Flask, request, jsonify
import jwt
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
expiration_delta = timedelta(days=1)


# Mock user data (replace with database)
users = {
    'user1': {'password': 'password1','role':'user'},
    'user2': {'password': 'password2','role':'admin'},
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username in users and password == users[username]['password']:
        payload = {
            'username': username,
            'role':users[username]['role'],
            'exp': datetime.utcnow() + expiration_delta
        }
        token = jwt.encode(payload, app.secret_key, algorithm='HS256')
        return jsonify({'token': token})

    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({'error': 'Token is missing'}), 401
    try:
        payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        return jsonify({'message': 'Access granted', 'username': payload['username']})
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

@app.route('/validate',methods=['POST'])
def validation():
    encoded_jwt = request.headers["Authorization"]
    
    if not encoded_jwt:
        return "missing credentials", 401
    try:
        decoded = jwt.decode(
            encoded_jwt, app.secret_key, algorithms=["HS256"]
        )
    except:
        return "not authorized", 403

    return decoded, 200


@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
