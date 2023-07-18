from flask import Flask, request, redirect, url_for, flash, session, jsonify, send_from_directory
from google_auth_oauthlib.flow import Flow
import os
from datetime import datetime
import config
import secrets
import psycopg2
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from get_events import get_events
from ChatAI import cv_chat

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
app.config['JSONIFY_MIMETYPE'] = 'application/json'


# Create a cursor object

secret_keyss = secrets.token_hex(16)
app.secret_key = secret_keyss


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Enable non-HTTPS for development

@app.route('/api/set_timezone', methods=['POST'])
def set_timezone():
    print('Received a request.')
    data = request.get_json()
    print('Data:', data)
    session['timezone'] = data['timezone']
    print('Timezone set:', session['timezone'])
    return {'message': 'Timezone set successfully.'}, 200


@app.route('/api/aichat', methods=['POST'])
def chat():
    chat = request.get_json()
    user_input = chat.get('userInput')
    response_message = cv_chat(user_input)

    return jsonify({'message': response_message}), 200


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if os.path.isfile(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        response = app.send_static_file('index.html')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

if __name__ == '__main__':

    app.run(debug=True)