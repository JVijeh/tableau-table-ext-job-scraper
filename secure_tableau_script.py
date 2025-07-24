# TabPy-compatible Job Scraper for Tableau
import pandas as pd
import http.client
import json
import time
import os
from dotenv import load_dotenv

# Load .env file (if available)
load_dotenv()

# Securely load environment variables
JOB_API_KEY = os.getenv("JOB_API_KEY")
DEFAULT_SEARCH_KEYWORDS = os.getenv("DEFAULT_SEARCH_KEYWORDS", "tableau")
DEFAULT_SEARCH_LOCATION = os.getenv("DEFAULT_SEARCH_LOCATION", "us")
DEFAULT_TARGET_JOBS = int(os.getenv("DEFAULT_TARGET_JOBS", "120"))
DEFAULT_MAX_PAGES = int(os.getenv("DEFAULT_MAX_PAGES", "4"))

# Validate credentials with helpful error message
if not JOB_API_KEY:
    df = pd.DataFrame({
        'Status': ['CREDENTIAL_ERROR'],
        'Issue': ['Missing JOB_API_KEY environment variable'],
        'Solution': ['Set JOB_API_KEY when starting TabPy: JOB_API_KEY=your_key tabpy'],
        'Timestamp': [pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')]
    })
    return df

# Initialize variables
website = 'jooble.org'
search_keywords = DEFAULT_SEARCH_KEYWORDS
search_location = DEFAULT_SEARCH_LOCATION
target_jobs = DEFAULT_TARGET_JOBS
max_pages = DEFAULT_MAX_PAGES
all_jobs = []
api_connected = False

# Collect jobs from multiple pages
for page in range(1, max_pages + 1):
    try:
        conn = http.client.HTTPConnection(website)
        headers = {"Content-type": "application/json"}
        search_data = {
            "keywords": search_keywords,
            "location": search_location,
            "page": page
        }
        conn.request("POST", "/api/" + JOB_API_KEY, json.dumps(search_data), headers)
        response = conn.getresponse()
        response_data = json.loads(response.read().decode('utf-8'))
        jobs_list = response_data.get("jobs", [])
        conn.close()
        
        api_connected = True  # Mark that we successfully connected
        
        if jobs_list:
            all_jobs.extend(jobs_list)
            if len(all_jobs) >= target_jobs:
                break
        else:
            break
            
        if page < max_pages:
            time.sleep(1)
            
    except Exception as e:
        break

# Handle no jobs found with enhanced diagnostics
if not all_jobs:
    if api_connected:
        issue_msg = f"API connected but found 0 jobs for '{search_keywords}' in '{search_location}'"
        solution_msg = "Try different search terms or location (us, uk, ca, au, etc.)"
    else:
        issue_msg = "Failed to connect to Jooble API"
        solution_msg = "Check internet connection and API key validity"
    
    df = pd.DataFrame({
        'Status': ['NO_JOBS_FOUND'],
        'Issue': [issue_msg],
        'Search_Keywords': [search_keywords],
        'Search_Location': [search_location],
        'Suggestion': [solution_msg],
        'API_Connected': [str(api_connected)],
        'Timestamp': [pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')]
    })
    return df

# Process job results
df = pd.DataFrame(all_jobs)

# Ensure all required columns exist
required_columns = ['id', 'title', 'company', 'location', 'snippet', 
                    'salary', 'type', 'source', 'link', 'updated']
for col in required_columns:
    if col not in df.columns:
        df[col] = 'N/A'

df = df[required_columns]
df = df.fillna('N/A')

# Convert all columns to string
for col in df.columns:
    df[col] = df[col].astype(str)

# Extract city/state
def extract_city_state(location_str):
    try:
        location_str = str(location_str).strip()
        if ',' in location_str:
            parts = location_str.split(',')
            return parts[0].strip(), parts[-1].strip()
        return location_str, 'N/A'
    except:
        return 'N/A', 'N/A'

df[['city', 'state']] = df['location'].apply(lambda x: pd.Series(extract_city_state(x)))

# Remove duplicates
df = df.drop_duplicates(subset=['id', 'title', 'company'], keep='first')

# Final column order
df = df[['id', 'title', 'company', 'location', 'city', 'state',
         'snippet', 'salary', 'type', 'source', 'link', 'updated']]

return df

# 🔒 SETUP INSTRUCTIONS:
# Start TabPy with: JOB_API_KEY=your_api_key tabpy
# Optional: JOB_API_KEY=your_key DEFAULT_SEARCH_KEYWORDS="data analyst" tabpy