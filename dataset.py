import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY = 'APIKEY'
CITY = 'Baku'
COUNTRY = 'Azerbaijan'
BASE_URL = 'http://api.worldweatheronline.com/premium/v1/past-weather.ashx'

end_date = datetime.today()
start_date = end_date - timedelta(days=5 * 365)

MAX_DAYS_PER_REQUEST = 35

def daterange(start_dt, end_dt, step_days):
    """Yield (start, end) tuples splitting the date range into chunks."""
    current_start = start_dt
    while current_start < end_dt:
        current_end = min(current_start + timedelta(days=step_days - 1), end_dt)
        yield current_start, current_end
        current_start = current_end + timedelta(days=1)

all_records = []

for chunk_start, chunk_end in daterange(start_date, end_date, MAX_DAYS_PER_REQUEST):
    params = {
        'key': API_KEY,
        'q': f"{CITY},{COUNTRY}",
        'date': chunk_start.strftime('%Y-%m-%d'),
        'enddate': chunk_end.strftime('%Y-%m-%d'),
        'tp': '24',               # Daily data
        'format': 'json'
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()
    
    for day in data['data']['weather']:
        record = {
            'date': day['date'],
            'maxtemp_C': day['maxtempC'],
            'mintemp_C': day['mintempC'],
            'avgtemp_C': day['avgtempC'],
            'totalSnow_cm': day.get('totalSnow_cm'),
            'sunHour': day.get('sunHour'),
            'uvIndex': day.get('uvIndex')
        }
        all_records.append(record)

df = pd.DataFrame(all_records)

df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

output_path = 'baku_past5years_weather.csv'
df.to_csv(output_path, index=False)

