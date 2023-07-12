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

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
app.config['JSONIFY_MIMETYPE'] = 'application/json'


conn = psycopg2.connect(
    host="ec2-3-210-173-88.compute-1.amazonaws.com",
    database="d88elb5iue4ieg",
    user="zbffwirdadngwj",
    password="bdbf0ec59f245e5f27d2e61401c1332e5a6c306145c28705e4dc66171a148a0d"
)

# Create a cursor object
cursor = conn.cursor()
secret_keyss = secrets.token_hex(16)
app.secret_key = secret_keyss


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Enable non-HTTPS for development

client_config = {
    "web": {
        "client_id": config.GOOGLE_CLIENT_ID,
        "client_secret": config.GOOGLE_CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": [
            "http://localhost:5000/callback"
        ],
    }
}

flow = Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/calendar",
        "openid",
        "https://www.googleapis.com/auth/calendar.readonly"],
    redirect_uri = "http://localhost:5000/callback")

@app.route('/api/set_timezone', methods=['POST'])
def set_timezone():
    print('Received a request.')
    data = request.get_json()
    print('Data:', data)
    session['timezone'] = data['timezone']
    print('Timezone set:', session['timezone'])
    return {'message': 'Timezone set successfully.'}, 200


def fetch_user_credentials(email):
    cursor.execute("SELECT * FROM auth_users WHERE email=%s", (email,))
    user = cursor.fetchone()
    if not user:
        return None

    creds = Credentials(
        token=None,
        refresh_token=user[5],
        client_id=config.GOOGLE_CLIENT_ID,
        client_secret=config.GOOGLE_CLIENT_SECRET,
        token_uri='https://oauth2.googleapis.com/token',
        scopes=['https://www.googleapis.com/auth/calendar']
    )

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return creds


@app.route('/login')
def login():
    # Generate URL for the user's browser to go to the start of the OAuth flow.
    authorization_url, state = flow.authorization_url(
        # This parameter enables offline access which gives your application
        # both an access and refresh token.
        access_type='offline',
        # This parameter enables incremental auth.
        include_granted_scopes='true')

    # Store the state in the user's session for later validation (optional).
    session['state'] = state

    # Redirect the user's browser to the OAuth 2.0 provider.
    return redirect(authorization_url)


@app.route('/callback')
def callback():
    print("Request URL:", request.url)
    print("Request args:", request.args)

    error = request.args.get('error', None)
    if error:
        error_description = request.args.get('error_description', None)
        print(f"Error: {error}. Description: {error_description}")
        return f"Error: {error}. Description: {error_description}", 400

    code = request.args.get('code', None)
    if code is None:
        return "Authorization code not found in the response. Please try again.", 400

    flow.fetch_token(code=code)
    credentials = flow.credentials


    auth_session = flow.authorized_session()

    # Retrieve user's profile information
    userinfo_endpoint = 'https://www.googleapis.com/oauth2/v1/userinfo'
    headers = {'Authorization': f'Bearer {credentials.token}'}
    userinfo = auth_session.get(userinfo_endpoint, headers=headers)
    userinfo_data = userinfo.json()
    print(userinfo_data)

    if userinfo_data:
        email = userinfo_data['email']
        first_name = userinfo_data['given_name']
        last_name = userinfo_data['family_name']
        refresh_token = credentials.refresh_token

        # Check if the user exists in the database
        cursor.execute("SELECT * FROM auth_users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if not user:
            # Create a new user in the database
            cursor.execute(
                "INSERT INTO auth_users (first_name, last_name, email, source, refresh_token) VALUES (%s, %s, %s, %s, %s)",
                (first_name, last_name, email, 'google', refresh_token))
            conn.commit()

            # Get the ID of the newly created user
            user_id = cursor.lastrowid

            # Add an entry to the calendar_ids table for this user
            cursor.execute(
                "INSERT INTO calendar_ids (email, calendarId, calendar_name, primary_cal) VALUES (%s, %s, %s, %s)",
                (email, email, 'primary', 'True')
            )
            conn.commit()
        else:
            user_id = user[0]

        # Store user data in the session
        session['user_id'] = user_id
        session['email'] = email
        session['first_name'] = first_name
        session['last_name'] = last_name

    else:
        print('Failed to get user info data:', userinfo.json())
        flash('Login failed. Please try again.', 'danger')
        return redirect(url_for('login'))

    # Check that the session variables were set
    if 'email' not in session:
        print('Failed to set email in session')
        flash('Login failed. Please try again.', 'danger')
        return redirect(url_for('login'))
    cursor.execute("SELECT calendarId, calendar_name FROM calendar_ids WHERE email=%s AND primary_cal='True'", (email,))
    primary_calendar = cursor.fetchone()
    print(f'Primary Calendar: {primary_calendar}')

    cursor.execute("SELECT calendarId, calendar_name FROM calendar_ids WHERE email=%s AND primary_cal='False'", (email,))
    secondary_calendar = cursor.fetchone()
    print(f'Secondary Calendar: {secondary_calendar[0]}')
    start_date = "01-01-2023 00-00-00"
    end_date = "07-07-2023 00-00-00"
    calendars = [primary_calendar, secondary_calendar]  # Each element is a tuple of (calendarId, calendar_name)
    events_list = []

    for calendar in calendars:
        calendar_id = calendar[0]  # Extract calendarId
        calendar_name = calendar[1]  # Extract calendar_name
        events = get_events(credentials=credentials, calendar_id=calendar_id, calendar_name=calendar_name,
                            start_date=start_date, end_date=end_date)
        events_list.append(events)

    print(events_list)
    flash('You have successfully logged in.', 'success')


    return redirect(url_for('catch_all', path=''))




@app.route('/api/user')
def user():
    if 'first_name' in session and 'last_name' in session:
        return jsonify({'first_name': session['first_name'], 'last_name': session['last_name']})
    else:
        return jsonify({'error': 'User not logged in'}), 401

@app.route('/api/add_calendar', methods=['POST'])
def add_calendar():
    data = request.get_json()
    calendar_name = data['name']
    calendarId = data['id']
    user_email = session['email']

    try:
        credentials = fetch_user_credentials(user_email)
        service = build('calendar', 'v3', credentials=credentials)
        service.calendars().get(calendarId=calendarId).execute()
    except Exception as e:
        print(f"Exception occurred while trying to validate calendarId: {e}")
        return jsonify({'message': 'Invalid calendar ID.'}), 400

    try:
        # Execute SQL INSERT command
        cursor.execute(
            "INSERT INTO calendar_ids (email, calendarId, calendar_name, primary_cal ) VALUES (%s, %s, %s, %s)",
            (user_email,calendarId, calendar_name, "False")
        )

        # Commit the transaction
        conn.commit()

        return jsonify({'message': 'Calendar added successfully!'}), 200
    except Exception as e:
        # Log the exception information for troubleshooting
        print(f"Exception occurred: {e}")
        return jsonify({'message': 'An error occurred while adding the calendar.', 'error': str(e)}), 500


@app.route('/api/aichat', methods=['POST'])
def chat():
    chat = request.get_json()
    user_email = session['email']
    user_credentials = fetch_user_credentials(user_email)
    user_input = chat.get('userInput')


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