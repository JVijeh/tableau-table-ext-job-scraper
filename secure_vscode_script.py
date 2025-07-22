# Import the tools we need
import pandas as pd      # This helps us work with tables of data (like Excel spreadsheets)
import http.client       # This helps us connect to websites
import json              # This helps us work with JSON data (a common web data format)
import time              # This helps us add delays between API calls to be respectful
from dotenv import load_dotenv  # This loads our API credentials from a .env file
import os                # This helps us work with environment variables (like our API key)     
from config import Config  # 🔒 SECURE: Load API credentials from environment variables

def get_job_data():
    """
    This function contains the exact same logic as the Tableau script,
    but wrapped in a function so we can use return statements in VS Code.
    """
    
    # DIAGNOSTIC VARIABLES: These will help us understand what went wrong if something fails
    error_message = "No errors - script executed successfully"
    api_response_received = False
    jobs_found_count = 0
    pages_fetched = 0

    # TRY-EXCEPT: This is used for error handling - if something goes wrong, we'll capture details
    try:
        # 🔒 CREDENTIAL VALIDATION: Check that API credentials are loaded before proceeding
        try:
            Config.validate_required_credentials()
            print("✅ API credentials loaded successfully!")
        except ValueError as cred_error:
            error_message = f"Missing API credentials: {cred_error}"
            # Return diagnostic data if credentials are missing
            diagnostic_data = {
                'Status': ['CREDENTIAL_ERROR'],
                'Issue': [error_message],
                'Solution': ['Create .env file with JOB_API_KEY=your_api_key_here'],
                'Required_Files': ['.env file with JOB_API_KEY'],
                'Current_API_Key': ['Not loaded from environment'],
                'Timestamp': [pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')],
                'Next_Steps': ['1. Copy .env.template to .env, 2. Add your API key, 3. Run again']
            }
            return pd.DataFrame(diagnostic_data), error_message, False, 0, 0
        
        # 🔒 API SETTINGS: Load securely from environment variables
        website = 'jooble.org'  # The website we're getting data from
        my_api_key = Config.JOB_API_KEY  # 🔒 SECURE: Loaded from .env file
        
        # SEARCH PARAMETERS: What we want to search for - you can change these to find different jobs
        # You can also set these in your .env file to avoid changing code
        search_keywords = Config.DEFAULT_SEARCH_KEYWORDS if hasattr(Config, 'DEFAULT_SEARCH_KEYWORDS') else "tableau"
        search_location = Config.DEFAULT_SEARCH_LOCATION
        target_jobs = Config.DEFAULT_TARGET_JOBS
        max_pages = Config.DEFAULT_MAX_PAGES
        
        print(f"🔍 Searching for: '{search_keywords}' in '{search_location}'")
        print(f"📊 Target: {target_jobs} jobs across max {max_pages} pages")
        
        # STORAGE CONTAINER: This list will hold all jobs from all pages
        all_jobs = []  # Think of this as an empty box where we'll collect jobs from each page
        
        # MULTI-PAGE LOOP: This fetches jobs from multiple pages to get 120+ records
        # Instead of getting just ~30 jobs from 1 page, we'll get jobs from up to 4 pages
        for page in range(1, max_pages + 1):  # Loop from page 1 to page 4
            try:
                print(f"📄 Fetching page {page}...")
                
                # STEP 1: Connect to the job website for this specific page
                # Think of this like opening a web browser and going to page 1, then page 2, etc.
                web_connection = http.client.HTTPConnection(website)
                
                # STEP 2: Set up our request headers
                # Headers are like the "envelope" information when sending a letter
                headers = {"Content-type": "application/json"}
                
                # STEP 3: Create our search request for this specific page
                # We put our search terms into a Python dictionary (like a mini-database)
                # Now we include the page number so we get different results each time
                search_data = {
                    "keywords": search_keywords, 
                    "location": search_location,
                    "page": page  # This tells the API which page of results we want
                }
                # Convert the dictionary to JSON format (the language websites understand)
                search_text = json.dumps(search_data)
                
                # STEP 4: Send our search request to the website
                # This is like submitting a search form on a website, but for a specific page
                web_connection.request('POST', '/api/' + my_api_key, search_text, headers)
                
                # STEP 5: Get the response from the website
                # The website sends back the job listings for this page
                response = web_connection.getresponse()
                response_text = response.read().decode('utf-8')  # Convert to readable text
                api_response_received = True  # Mark that we got a response
                pages_fetched = page  # Keep track of how many pages we've successfully fetched
                
                # STEP 6: Convert the response from JSON back to Python data
                # JSON is how websites send data, but we need to convert it to use in Python
                response_data = json.loads(response_text)
                
                # STEP 7: Extract the job listings from this page's response
                # The website sends back lots of info, but we only want the "jobs" part
                jobs_list = response_data.get("jobs", [])
                # NOTE: .get("jobs", []) means "get the jobs, but if there aren't any, give me an empty list"
                
                # STEP 8: Close our connection to the website (like closing a web browser)
                web_connection.close()
                
                # STEP 9: Check if we got any jobs back from this page
                if jobs_list:  # If we found jobs on this page
                    print(f"✅ Found {len(jobs_list)} jobs on page {page}")
                    # ADD JOBS TO OUR COLLECTION: Extend means "add all these jobs to our existing list"
                    all_jobs.extend(jobs_list)  # This is like adding more items to our collection box
                    
                    # CHECK IF WE HAVE ENOUGH JOBS: If we've reached our target, we can stop
                    if len(all_jobs) >= target_jobs:
                        print(f"🎯 Reached target of {target_jobs} jobs! Stopping early.")
                        break  # Exit the loop early - we have enough jobs!
                else:
                    print(f"❌ No jobs found on page {page}")
                    # NO JOBS ON THIS PAGE: If this page has no jobs, probably no point checking more pages
                    break  # Exit the loop - no more jobs available
                    
                # PURPOSEFUL DELAY: Wait 1 second before requesting the next page
                # This is being respectful to the API server - don't overwhelm it with requests
                if page < max_pages:  # Only add delay if we're not on the last page
                    time.sleep(1)  # Wait 1 second
                    
            except Exception as page_error:
                print(f"⚠️ Error on page {page}: {page_error}")
                # IF THIS PAGE FAILS: Don't let one bad page ruin everything
                # Just stop trying more pages and work with what we have
                break
        
        # COUNT TOTAL JOBS: Keep track of how many jobs we collected across all pages
        jobs_found_count = len(all_jobs)
        print(f"📊 Total jobs collected: {jobs_found_count}")
        
        # STEP 10: Process the collected jobs (only if we found some)
        if all_jobs:  # If we successfully collected jobs from any pages
            # STEP 11: Convert all job data into a table format using pandas
            # Pandas is like Excel for Python - it helps us organize data in rows and columns
            df = pd.DataFrame(all_jobs)
            
            # STEP 12: Make sure we have all the columns we need
            # Sometimes the API doesn't send all the data we expect
            required_columns = ['id', 'title', 'company', 'location', 'snippet', 
                               'salary', 'type', 'source', 'link', 'updated']
            
            # Check each column and add it if it's missing
            for column in required_columns:
                if column not in df.columns:
                    df[column] = 'N/A'  # Fill missing columns with "N/A"
            
            # STEP 13: Keep only the columns we want (remove any extra ones)
            df = df[required_columns]
            
            # STEP 14: Clean up the data - replace any empty cells with 'N/A'
            # Sometimes APIs send empty values, which can cause problems
            df = df.fillna('N/A')
            
            # STEP 15: Make sure all data is in text format
            # Tableau works best when all data is text (strings)
            for column in df.columns:
                df[column] = df[column].astype(str)  # Convert everything to text
            
            # STEP 16: EXTRACT CITY AND STATE FROM LOCATION
            # This function takes a location like "Seattle, WA" and splits it into city and state
            def extract_city_state(location_str):
                """
                This function takes a location string and tries to split it into city and state.
                Examples:
                - "Seattle, WA" becomes city="Seattle", state="WA"
                - "New York" becomes city="New York", state="N/A"
                - Empty/invalid becomes city="N/A", state="N/A"
                """
                try:
                    # Convert to string and remove extra spaces
                    location_str = str(location_str).strip()
                    
                    # CHECK IF LOCATION HAS A COMMA: Most US locations are formatted as "City, State"
                    if ',' in location_str:
                        # SPLIT BY COMMA: Break "Seattle, WA" into ["Seattle", " WA"]
                        parts = location_str.split(',')
                        city = parts[0].strip()    # Take first part as city, remove spaces
                        state = parts[-1].strip()  # Take last part as state, remove spaces
                        return city, state
                    else:
                        # NO COMMA FOUND: Treat entire string as city, no state info
                        return location_str, 'N/A'
                except:
                    # IF ANYTHING GOES WRONG: Return safe default values
                    return 'N/A', 'N/A'
            
            # APPLY CITY/STATE EXTRACTION: Use our function on every location
            # This creates two new columns: 'city' and 'state'
            df[['city', 'state']] = df['location'].apply(lambda x: pd.Series(extract_city_state(x)))
            
            # STEP 17: Remove duplicate jobs
            # Sometimes the same job appears on multiple pages, so we remove duplicates
            # We consider jobs duplicates if they have the same ID, title, and company
            original_count = len(df)
            df = df.drop_duplicates(subset=['id', 'title', 'company'], keep='first')
            duplicates_removed = original_count - len(df)
            if duplicates_removed > 0:
                print(f"🧹 Removed {duplicates_removed} duplicate jobs")
            
            # STEP 18: Organize final columns in a logical order
            # Put city and state right after location so they're easy to see
            final_columns = ['id', 'title', 'company', 'location', 'city', 'state', 
                            'snippet', 'salary', 'type', 'source', 'link', 'updated']
            df = df[final_columns]
                
        else:  # If we didn't get any jobs from any pages
            # CREATE DIAGNOSTIC INFORMATION: Help the user understand what happened
            if api_response_received:
                error_message = f"API connected successfully but found 0 jobs for '{search_keywords}' in '{search_location}' across {pages_fetched} pages. Try different search terms or location."
            else:
                error_message = "Failed to connect to the Jooble API. Check internet connection and API key."
            
            # Create a diagnostic table with detailed information about what went wrong
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
                'API_Key_First_4_Chars': [my_api_key[:4] + '...'],
                'Timestamp': [pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')],
                'Next_Steps': ['Try broader search terms or different location codes (us, uk, ca, au, etc.)']
            }
            df = pd.DataFrame(diagnostic_data)

    # EXCEPTION HANDLING: If anything goes wrong above, this code runs instead
    except Exception as e:
        # Capture the specific error that occurred
        error_message = f"Python error: {str(e)}"
        print(f"❌ Error occurred: {error_message}")
        
        # Create detailed diagnostic information about the Python error
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
            'Common_Solutions': ['Verify TabPy connection, check firewall settings, or try simpler search terms']
        }
        df = pd.DataFrame(diagnostic_data)

    # IMPORTANT (FYI): Return the data (this works in VS Code because it's inside a function)
    return df, error_message, api_response_received, pages_fetched, jobs_found_count

# FOR VS CODE TESTING: Execute the function and show detailed results
if __name__ == "__main__":
    print("=== RUNNING SECURE JOB SCRAPER IN VS CODE ===")
    print("🔒 Using environment variables for API credentials")
    
    # Call the function
    result_df, error_msg, api_received, pages_done, jobs_count = get_job_data()
    
    print(f"API Response Received: {api_received}")
    print(f"Pages Fetched: {pages_done}")
    print(f"Jobs Found: {jobs_count}")
    print(f"DataFrame shape: {result_df.shape}")
    
    if len(result_df) > 0:
        if 'Status' in result_df.columns:
            print("\nDiagnostic mode - showing issues:")
            for i, row in result_df.iterrows():
                print(f"  {row.get('Status', 'Unknown')}: {row.get('Issue', 'No details')}")
        else:
            print(f"\nSUCCESS: Found {len(result_df)} jobs!")
            print("\nSample jobs:")
            for i in range(min(5, len(result_df))):
                job_info = f"  {i+1}. {result_df.iloc[i]['title']} at {result_df.iloc[i]['company']} ({result_df.iloc[i]['location']})"
                print(job_info)
            
            if 'city' in result_df.columns:
                print(f"\nCity/State extraction examples:")
                for i in range(min(3, len(result_df))):
                    location_info = f"  {result_df.iloc[i]['location']} → City: {result_df.iloc[i]['city']}, State: {result_df.iloc[i]['state']}"
                    print(location_info)
            
            print(f"\nColumns available: {list(result_df.columns)}")
    
    print(f"\nError message: {error_msg}")
    print("=== END VS CODE EXECUTION ===")
    print("\nNOTE: For Tableau, use the separate secure Tableau Analytics Extension script.")

# 🔒 SECURITY UPGRADE NOTES:
# ========================
# This version now loads API credentials securely from environment variables:
# 1. API key comes from .env file (JOB_API_KEY=your_key_here)
# 2. Search parameters can be set in .env file or use defaults
# 3. Credential validation happens before making any API calls
# 4. Better error handling for missing credentials
# 5. Same functionality as before, but secure for sharing

# BEGINNER NOTES AND CUSTOMIZATION GUIDE:
# =====================================

# 🔒 SECURE CONFIGURATION (NEW!):
# ===============================
# Instead of changing code, you can now set these in your .env file:
# JOB_API_KEY=your_api_key_here                    # Required: Your Jooble API key
# DEFAULT_SEARCH_KEYWORDS=tableau                  # Optional: What to search for
# DEFAULT_SEARCH_LOCATION=us                       # Optional: Where to search
# DEFAULT_TARGET_JOBS=120                          # Optional: How many jobs to get
# DEFAULT_MAX_PAGES=4                              # Optional: Max pages to try

# KEY VARIABLES YOU CAN STILL MODIFY (located in the get_job_data function above):
# ============================================================================
# These will override .env settings if you change them in the code:
# search_keywords = "tableau"     # What to search for (try: "data analyst", "python", "sql")
# search_location = "us"          # Where to search (try: "uk", "ca", "au", "de", "fr")
# target_jobs = 120              # Minimum number of jobs to fetch
# max_pages = 4                  # Maximum pages to try

# 🔒 SETUP REQUIREMENTS (NEW!):
# =============================
# 1. Install: pip install python-dotenv
# 2. Copy .env.template to .env
# 3. Add your API key to .env file: JOB_API_KEY=your_actual_key
# 4. Run this script - it will automatically load your credentials securely

# OUTPUT FORMAT - WHAT COLUMNS YOU'LL GET:
# ========================================
# The final DataFrame includes these columns in this exact order:
# 1.  id          - Job ID number (unique identifier)
# 2.  title       - Job title (e.g., "Senior Data Analyst")
# 3.  company     - Company name (e.g., "Microsoft")
# 4.  location    - Original location from API (e.g., "Seattle, WA")
# 5.  city        - Extracted city name (e.g., "Seattle")
# 6.  state       - Extracted state/region (e.g., "WA")
# 7.  snippet     - Job description preview
# 8.  salary      - Salary information (if available)
# 9.  type        - Job type (Full-time, Part-time, Contract, etc.)
# 10. source      - Where the job was originally posted
# 11. link        - Direct link to the job posting
# 12. updated     - When the job was last updated