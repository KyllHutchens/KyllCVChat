import datetime
import requests

url = "https://api.wit.ai/message"

prompt = "What events do I have on in June?"

params = {
    'v': '20230710',
    'q': prompt,
    'timezone': 'Your Timezone'  # Replace with your desired timezone
}
headers = {
    'Authorization': 'Bearer TAGT65U33RZ4YZXIBKFW6CREREBNRTU4'
}

response = requests.get(url, params=params, headers=headers)
data = response.json()

# Retrieve the type, grain, and interval values from the entities
datetime_entities = data['entities'].get('wit$datetime:datetime', [])
if datetime_entities:
    type_entity = datetime_entities[0]['type']
    grain_entity = datetime_entities[0]['from']['grain']
    start_date_entity = datetime_entities[0]['from']['value']
    end_date_entity = datetime_entities[0]['to']['value']
else:
    type_entity = None

if type_entity == 'interval':
    # Determine the start and end dates from the interval
    start_date = datetime.datetime.strptime(start_date_entity, "%Y-%m-%dT%H:%M:%S.%f%z")
    end_date = datetime.datetime.strptime(end_date_entity, "%Y-%m-%dT%H:%M:%S.%f%z")

    # Format the start and end dates
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    # Perform further processing with start_date_str and end_date_str
    print('Start Date:', start_date_str)
    print('End Date:', end_date_str)
elif type_entity is None:
    # Handle the case when no datetime value is provided
    start_date = datetime.datetime.now()
    end_date = start_date + datetime.timedelta(weeks=1)

    # Format the start and end dates
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    # Perform further processing with start_date_str and end_date_str
    print('Start Date (Default):', start_date_str)
    print('End Date (Default):', end_date_str)
else:
    # Handle the case when the type is not "interval"
    grain_value = datetime_entities[0]['grain']
    datetime_value = datetime_entities[0]['value']

    if grain_value == 'week':
        # Determine the start and end dates for the week
        start_date = datetime.datetime.strptime(datetime_value, "%Y-%m-%dT%H:%M:%S.%f%z")
        end_date = start_date + datetime.timedelta(weeks=1)

        # Format the start and end dates
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        # Perform further processing with start_date_str and end_date_str
        print('Start Date:', start_date_str)
        print('End Date:', end_date_str)
    elif grain_value == 'month':
        # Extract the month value from the datetime string
        month_value = datetime_value[5:7]

        # Get the last day of the month
        year = int(datetime_value[:4])
        last_day = calendar.monthrange(year, int(month_value))[1]

        # Format the start and end dates
        start_date_str = f'{year}-{month_value}-01'
        end_date_str = f'{year}-{month_value}-{last_day}'

        # Perform further processing with start_date_str and end_date_str
        print('Start Date:', start_date_str)
        print('End Date:', end_date_str)
    else:
        print('Grain value is not "week" or "month".')