from googleapiclient.discovery import build
from datetime import datetime
from pytz import UTC
from flask import session
from pytz import timezone as pytz_timezone

def get_events(credentials, calendar_id, calendar_name, start_date, end_date):
    # Build the service
    service = build('calendar', 'v3', credentials=credentials)

    # Get Timezone from session
    timezone = session.get('timezone')

    # Convert timezone string to pytz timezone object
    timezone = pytz_timezone(timezone)

    # Convert string dates to datetime objects with the session's timezone
    start_date = datetime.strptime(start_date, "%d-%m-%Y %H-%M-%S")
    start_date = timezone.localize(start_date)
    end_date = datetime.strptime(end_date, "%d-%m-%Y %H-%M-%S")
    end_date = timezone.localize(end_date)

    # Convert dates to UTC
    start_date_utc = start_date.astimezone(UTC)
    end_date_utc = end_date.astimezone(UTC)

    # Format dates to strings in the required format
    start_date_str = start_date_utc.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
    end_date_str = end_date_utc.strftime("%Y-%m-%dT%H:%M:%S") + "Z"

    print(timezone)

    # Use the Calendar API to get events
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_date_str,
        timeMax=end_date_str,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    event_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        all_day = 'date' in event['start']

        # Convert to datetime
        start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z") if not all_day else datetime.strptime(start, "%Y-%m-%d")
        end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S%z") if not all_day else datetime.strptime(end, "%Y-%m-%d")

        # If not all day event, convert to user's timezone
        if not all_day:
            start = start.astimezone(timezone)
            end = end.astimezone(timezone)
        summary = event.get('summary', '')
        event_info = {
            'calendar_name': calendar_name,
            'summary': summary,
            'start_time': start.time().strftime("%H:%M") if not all_day else None,
            'end_time': end.time().strftime("%H:%M") if not all_day else None,
            'start_date': start.date().strftime("%d-%m-%Y"),
            'end_date': end.date().strftime("%d-%m-%Y"),
            'all_day': all_day
        }

        event_list.append(event_info)

    return event_list