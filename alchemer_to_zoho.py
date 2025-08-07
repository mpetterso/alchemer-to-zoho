import os
import requests
import pandas as pd
import io

# Fetch secrets from environment variables
API_KEY = os.getenv('ALCHEMER_API_KEY')
API_SECRET = os.getenv('ALCHEMER_API_SECRET')
SURVEY_ID = os.getenv('ALCHEMER_SURVEY_ID')

ZOHO_IMPORT_URL = os.getenv('ZOHO_IMPORT_URL')
ZOHO_AUTH_TOKEN = os.getenv('ZOHO_AUTH_TOKEN')

params = {
    'api_token': API_KEY,
    'api_token_secret': API_SECRET,
    'resultsperpage': 100,
    'page': 1
}

all_responses = []

print("📥 Fetching data from Alchemer...")

while True:
    response = requests.get(f"https://api.alchemer.com/v5/survey/{SURVEY_ID}/surveyresponse", params=params)
    data = response.json()
    if 'data' not in data or not data['data']:
        break
    all_responses.extend(data['data'])
    params['page'] += 1

df = pd.DataFrame(all_responses)
csv_data = df.to_csv(index=False)

print("📤 Uploading to Zoho Analytics...")
files = {
    'FILE': ('alchemer_data.csv', io.StringIO(csv_data), 'text/csv')
}

headers = {
    'Authorization': f'Zoho-oauthtoken {ZOHO_AUTH_TOKEN}'
}

zoho_params = {
    'ZOHO_ACTION': 'IMPORT',
    'ZOHO_IMPORT_TYPE': 'TRUNCATEADD',  # replace existing data
    'ZOHO_AUTO_IDENTIFY': 'true',
    'ZOHO_ON_IMPORT_ERROR': 'ABORT'
}

upload_response = requests.post(ZOHO_IMPORT_URL, headers=headers, files=files, data=zoho_params)

if upload_response.status_code == 200:
    print("✅ Data uploaded successfully!")
else:
    print(f"❌ Upload failed: {upload_response.text}")
