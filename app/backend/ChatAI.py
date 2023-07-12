import requests
import openai
from get_events import get_events
from datetime import datetime
import re
import pytz

def get_intent(prompt , credentials):
    openai.api_key = "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"
    url = "https://api.wit.ai/message"
    params = {
        'v': '20230710',
        'q': prompt
    }
    headers = {
        'Authorization: Bearer TAGT65U33RZ4YZXIBKFW6CREREBNRTU4'
    }

    response = requests.get(url, params=params, headers=headers)

    # The 'response' object now contains the server's response to your request.
    # You can access the response body (as JSON) using response.json():
    data = response.json()
    if data.get('intents'):  # check if intents exist
        intent_type = data['intents'][0]['name']


        if intent_type == "get_events":
            retrieve_events(data, credentials, person)  # Pass 'data' as an argument
    else:
        print("No intent detected")
    return data


def retrieve_events(data, credentials):
    print(data)
    person = data['entities']['Person:Person'][0]['value']

    start_datetime_str = None
    end_datetime_str = None
    if data['entities'].get('wit$datetime:datetime'):
        if data['entities']['wit$datetime:datetime'][0]['values'][0].get('from'):
            start_datetime_str = data['entities']['wit$datetime:datetime'][0]['values'][0]['from']['value']
        if data['entities']['wit$datetime:datetime'][0]['values'][0].get('to'):
            end_datetime_str = data['entities']['wit$datetime:datetime'][0]['values'][0]['to']['value']

    start_date = datetime.fromisoformat(start_datetime_str).date() if start_datetime_str else None
    end_date = datetime.fromisoformat(end_datetime_str).date() if end_datetime_str else None
    start_time = datetime.fromisoformat(start_datetime_str).time() if start_datetime_str else None
    end_time = datetime.fromisoformat(end_datetime_str).time() if end_datetime_str else None

    events = get_events(start_date, end_date, credentials)
    timezone = get_timezone(credentials)
    formatted_events = []
    for event in events:
        start_date_local, start_time_local = convert_to_local_timezone(event["start"].split("T")[0], event["start_time"], timezone)
        end_date_local, end_time_local = convert_to_local_timezone(event["end"].split("T")[0], event["end_time"], timezone)

        event_dict = {
            "all_day_event": str(event["all_day_event"]),
            "end": end_date_local.isoformat(),
            "end_time": end_time_local.isoformat(),
            "start": start_date_local.isoformat(),
            "start_time": start_time_local.isoformat(),
            "summary": event["summary"],
            "calendar_name": "John"  # You may need to modify this to get the actual calendar name
        }
        print(event_dict)
        if person is None or event['calendar_name'] == person:
            formatted_events.append(event_dict)
    for event in formatted_events:
        if event['all_day_event'] == 'True':
            event['all_day_event_note'] = 'This is an all day event.'
        else:
            event['all_day_event_note'] = ''

    if len(formatted_events) > 0:
        print(f"Matching events for {person if person else 'you'} between {start_date} and {end_date}:")
        for event in formatted_events:
            print(event)
    else:
        print(f"No matching events found for {person if person else 'all staff'} between {start_date} and {end_date}.")

    assistant_initial_message = f'I am trying to manage my calendar, which includes the following events:\n'
    for event in formatted_events:
        date = datetime.strptime(event['start'], "%Y-%m-%d").strftime("%d %b %Y")
        assistant_initial_message += f"- {event['summary']} starts at {event['start_time']} and ends at {event['end_time']} on {date}. {event['all_day_event_note']}\n"
    print(assistant_initial_message)

    assistant_return_message = f'Sure, I can help you manage those events. Based on the details provided, you have the event(s): \n'
    for event in formatted_events:
        date = datetime.strptime(event['start'], "%Y-%m-%d").strftime("%d %b %Y")
        assistant_return_message += f"- {event['summary']} starts at {event['start_time']} and ends at {event['end_time']} on {date}. {event['all_day_event_note']}\n"

    return formatted_events, assistant_initial_message, assistant_return_message
