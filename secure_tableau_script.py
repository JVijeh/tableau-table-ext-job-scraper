import pandas as pd
import http.client
import json
import time
from config import Config

error_message = "Unknown error occurred"
api_response_received = False
jobs_found_count = 0
pages_fetched = 0

try:
    # 🔒 CREDENTIAL VALIDATION: Check API credentials before proceeding
    try:
        Config.validate_required_credentials()
    except ValueError as cred_error:
        # Return diagnostic data if credentials are missing
        diagnostic_data = {
            'Status': ['CREDENTIAL_ERROR'],
            'Issue': [f"Missing API credentials: {cred_error}"],
            'Solution': ['Create .env file with JOB_API_KEY=your_api_key_here'],
            'Required_Files': ['.env file with JOB_API_KEY'],
            'Setup_Steps': ['1. Copy .env.template to .env', '2. Add your Jooble API key', '3. Refresh this data source'],
            'Documentation': ['See project README for complete setup instructions'],
            'Timestamp': [pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')]
        }
        df = pd.DataFrame(diagnostic_data)
    else:
        # 🔒 SECURE API SETTINGS: Load from environment variables
        website = 'jooble.org'
        my_api_key = Config.JOB_API_KEY  # 🔒 Loaded securely from .env file
        
        # SEARCH PARAMETERS: Load from config or use defaults
        search_keywords = getattr(Config, 'DEFAULT_SEARCH_KEYWORDS', 'tableau')
        search_location = Config.DEFAULT_SEARCH_LOCATION
        target_jobs = Config.DEFAULT_TARGET_JOBS
        max_pages = Config.DEFAULT_MAX_PAGES
        
        all_jobs = []
        
        for page in range(1, max_pages + 1):
            try:
                web_connection = http.client.HTTPConnection(website)
                headers = {"Content-type": "application/json"}
                
                search_data = {
                    "keywords": search_keywords, 
                    "location": search_location,
                    "page": page
                }
                search_text = json.dumps(search_data)
                
                web_connection.request('POST', '/api/' + my_api_key, search_text, headers)
                
                response = web_connection.getresponse()
                response_text = response.read().decode('utf-8')
                api_response_received = True
                pages_fetched = page
                
                response_data = json.loads(response_text)
                jobs_list = response_data.get("jobs", [])
                
                web_connection.close()
                
                if jobs_list:
                    all_jobs.extend(jobs_list)
                    if len(all_jobs) >= target_jobs:
                        break
                else:
                    break
                    
                if page < max_pages:
                    time.sleep(1)
                    
            except Exception as page_error:
                break
        
        jobs_found_count = len(all_jobs)
        
        if all_jobs:
            df = pd.DataFrame(all_jobs)
            required_columns = ['id', 'title', 'company', 'location', 'snippet', 'salary', 'type', 'source', 'link', 'updated']
            
            for column in required_columns:
                if column not in df.columns:
                    df[column] = 'N/A'
            
            df = df[required_columns]
            df = df.fillna('N/A')
            
            for column in df.columns:
                df[column] = df[column].astype(str)
            
            def extract_city_state(location_str):
                try:
                    location_str = str(location_str).strip()
                    if ',' in location_str:
                        parts = location_str.split(',')
                        city = parts[0].strip()
                        state = parts[-1].strip()
                        return city, state
                    else:
                        return location_str, 'N/A'
                except:
                    return 'N/A', 'N/A'
            
            df[['city', 'state']] = df['location'].apply(lambda x: pd.Series(extract_city_state(x)))
            df = df.drop_duplicates(subset=['id', 'title', 'company'], keep='first')
            
            final_columns = ['id', 'title', 'company', 'location', 'city', 'state', 'snippet', 'salary', 'type', 'source', 'link', 'updated']
            df = df[final_columns]
                
        else:
            if api_response_received:
                error_message = "API connected successfully but found 0 jobs for " + search_keywords + " in " + search_location + " across " + str(pages_fetched) + " pages. Try different search terms or location."
            else:
                error_message = "Failed to connect to the Jooble API. Check internet connection and API key."
            
            diagnostic_data = {
                'Status': ['ERROR'],
                'Issue': [error_message],
                'Search_Keywords': [search_keywords],
                'Search_Location': [search_location],
                'Target_Jobs': [str(target_jobs)],
                'Pages_Attempted': [str(max_pages)],
                'Pages_Fetched': [str(pages_fetched)],
                'API_Response_Received': [str(api_response_received)],
                'Jobs_Found': [str(jobs_found_count)],
                'Suggestion': ['Check search terms, location, internet connection, or API key'],
                'API_Key_Status': ['Loaded from environment variables'],
                'Timestamp': [pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')],
                'Next_Steps': ['Try broader search terms or different location codes (us, uk, ca, au, etc.)']
            }
            df = pd.DataFrame(diagnostic_data)

except Exception as e:
    error_message = "Python error: " + str(e)
    
    diagnostic_data = {
        'Status': ['PYTHON_ERROR'],
        'Error_Type': [type(e).__name__],
        'Error_Message': [str(e)],
        'Search_Keywords': [search_keywords if 'search_keywords' in locals() else 'Not set'],
        'Search_Location': [search_location if 'search_location' in locals() else 'Not set'],
        'Target_Jobs': [str(target_jobs) if 'target_jobs' in locals() else '120'],
        'Pages_Attempted': [str(max_pages) if 'max_pages' in locals() else '4'],
        'Pages_Fetched': [str(pages_fetched)],
        'API_Response_Received': [str(api_response_received)],
        'Jobs_Found': [str(jobs_found_count)],
        'Troubleshooting': ['Check: 1) Internet connection, 2) API key validity, 3) Search parameters'],
        'Timestamp': [pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')],
        'Common_Solutions': ['Verify TabPy connection, check firewall settings, or try simpler search terms'],
        'Security_Note': ['API credentials now loaded securely from environment variables']
    }
    df = pd.DataFrame(diagnostic_data)

return df

# 🔒 SECURITY UPGRADE - TABLEAU ANALYTICS EXTENSION VERSION
# ========================================================
# This script now loads API credentials securely from environment variables.
# 
# SETUP REQUIRED:
# 1. Install: pip install python-dotenv
# 2. Copy .env.template to .env  
# 3. Add your API key: JOB_API_KEY=your_actual_key_here
# 4. Place config.py in the same directory as this script
# 5. Use this script in Tableau Analytics Extensions
#
# BENEFITS:
# ✅ API key no longer visible in script
# ✅ Safe to share publicly on GitHub
# ✅ Easy to change credentials without editing code
# ✅ Follows industry security best practices
# ✅ Same functionality as original script
#
# CONFIGURATION:
# You can set these in your .env file:
# - JOB_API_KEY=your_key_here (required)
# - DEFAULT_SEARCH_LOCATION=us (optional)
# - DEFAULT_TARGET_JOBS=120 (optional) 
# - DEFAULT_MAX_PAGES=4 (optional)
#
# If credentials are missing, script returns helpful diagnostic information
# instead of failing silently.