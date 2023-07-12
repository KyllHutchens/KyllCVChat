# google_calendar.py
import pytz
from datetime import datetime, time
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

import config
from dateutil.parser import parse
import psycopg2
conn = psycopg2.connect(
    host="ec2-3-210-173-88.compute-1.amazonaws.com",
    database="d88elb5iue4ieg",
    user="zbffwirdadngwj",
    password="bdbf0ec59f245e5f27d2e61401c1332e5a6c306145c28705e4dc66171a148a0d"
)

cursor = conn.cursor()




def get_timezone(credentials):
    service = build('calendar', 'v3', credentials=credentials)

    try:
        calendar = service.calendars().get(calendarId='primary').execute()
        return calendar.get('timeZone', 'UTC')
    except HttpError as error:
        print(f"An error occurred: {error}")
        return 'UTC'

def get_events(start_date, end_date, credentials, calendarId=None):
    if not calendarId or calendarId == 'undefined':
        calendarId = 'primary'
    # Get the local timezone from the user's credentials
    user_timezone = get_timezone(credentials)
    local_timezone = pytz.timezone(user_timezone)

    # Convert the local date to a timezone-aware datetime object
    start_date_local = local_timezone.localize(datetime.combine(start_date, time.min))
    end_date_local = local_timezone.localize(datetime.combine(end_date, time.max))

    # Convert the local datetime to a UTC datetime
    start_date_utc = start_date_local.astimezone(pytz.UTC)
    end_date_utc = end_date_local.astimezone(pytz.UTC)

    # Format the UTC datetime for the calendar API
    start_date = start_date_utc.isoformat()
    end_date = end_date_utc.isoformat()

    service = build('calendar', 'v3', credentials=credentials)

    try:
        events_result = service.events().list(calendarId=calendarId, timeMin=start_date,
                                              timeMax=end_date, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        formatted_events = []

        for event in events:
            start = event['start'].get('dateTime') or event['start'].get('date')
            end = event['end'].get('dateTime') or event['end'].get('date')

            if start and end:
                start_dt = parse(start).astimezone(pytz.UTC)
                end_dt = parse(end).astimezone(pytz.UTC)

                all_day_event = 'date' in event['start']

                formatted_start = start_dt.isoformat()
                formatted_end = end_dt.isoformat()

                start_time = start_dt.strftime("%H:%M")
                end_time = end_dt.strftime("%H:%M")
                print(start_time)
                formatted_event = {
                    "summary": event.get("summary", "No title"),
                    "start": formatted_start,
                    "end": formatted_end,
                    "start_time": start_time,
                    "end_time": end_time,
                    "all_day_event": all_day_event
                }
                formatted_events.append(formatted_event)
            else:
                print(f"Skipped event {event.get('id')} due to missing start or end date.")

        return formatted_events
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []



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


def check_availability(user_email, start_datetime, end_datetime, credentials, calendarId=None):
    if not calendarId or calendarId == 'undefined':
        calendarId = 'primary'
    service = build('calendar', 'v3', credentials=credentials)

    freebusy_query = {
        'timeMin': start_datetime,
        'timeMax': end_datetime,
        'timeZone': get_timezone(credentials),
        'items': [{'id': user_email}]
    }

    try:
        response = service.freebusy().query(body=freebusy_query).execute()
        busy_slots = response['calendars'][user_email]['busy']
        return len(busy_slots) == 0
    except HttpError as error:
        print(f"An error occurred: {error}")
        return False



