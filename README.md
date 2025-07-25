# Tableau Analytics Extensions Job Scraper

**Automatically collect 120+ job listings with geographic parsing for Tableau analysis**

Transform manual job data collection into an automated, refreshable Tableau data source using Analytics Extensions. This script connects to job APIs, cleans the data, and delivers it to Tableau with enhanced geographic fields - all without leaving your Tableau workflow.


## 🔒 **Security First**

This project uses **secure environment variables** to protect API credentials. Your API keys are never visible in the code and are safe to share on GitHub.

---

## 🎯 **Perfect for Tableau Users Who Want To:**

✅ **Eliminate manual data entry** - No more copying and pasting job listings  
✅ **Connect to APIs without native connectors** - Access any REST API from Tableau  
✅ **Get refreshable data sources** - Updates automatically like any Tableau connection  
✅ **Enhance data during collection** - Split locations, remove duplicates, handle missing values  
✅ **Scale beyond basic web connectors** - Custom logic for complex data processing  

---

## 📊 **What This Script Delivers**

| Feature | Benefit | Tableau Impact |
|---------|---------|----------------|
| **120+ Job Records** | 4x more data than single API calls | More comprehensive analysis |
| **City/State Parsing** | Geographic dimensions from location strings | Enable state-level filtering and mapping |
| **Duplicate Removal** | Clean, unique job listings | Accurate counts and metrics |
| **Error Diagnostics** | Clear troubleshooting information | Reliable production refreshes |
| **Configurable Search** | Easy parameter changes via environment variables | Adapt for different job markets |
| **🔒 Secure Credentials** | API keys protected in environment variables | Safe for public repositories |

---

## 🚀 **Quick Start for Tableau Users**

### **Prerequisites**
- **Tableau Desktop 2024.1+** (or Tableau Server with TabPy configured)
- **Python 3.7+** with pip
- **Jooble API key** (free registration at [jooble.org](https://jooble.org))

### **🔒 Security Setup (Required First Step)**

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   *This installs TabPy, pandas, requests, and python-dotenv*

2. **Create Your Secure Configuration**
   ```bash
   # Copy the template to create your private config
   cp .env.template .env
   ```

3. **Add Your API Credentials**
   Edit the `.env` file and replace the placeholder:
   ```env
   # Required: Your Jooble API key
   JOB_API_KEY=your_actual_jooble_api_key_here
   
   # Optional: Customize default search parameters
   DEFAULT_SEARCH_KEYWORDS=tableau
   DEFAULT_SEARCH_LOCATION=us
   DEFAULT_TARGET_JOBS=120
   DEFAULT_MAX_PAGES=4
   ```

   **🚨 Important:** Never commit the `.env` file to version control. It's protected by `.gitignore`.

### **⚡ Tableau Integration**

4. **Install and Start TabPy** (one-time setup)
   ```bash
   pip install tabpy
   tabpy
   ```
   *TabPy will start on localhost:9004*

5. **Configure Tableau Analytics Extension**
   - In Tableau: **Help → Settings and Performance → Manage Analytics Extension Connection**
   - **Server**: `localhost`
   - **Port**: `9004`
   - **Test Connection** (should show "Successfully connected")

6. **Add the Script as Data Source**
   - **Connect to Data → More → Analytics Extensions**
   - **Copy and paste** the entire contents of `table_extension_job_search-tableau_only_SECURE.py`
   - **Click OK** - Tableau will execute the script and create your data source

7. **Start Building Visualizations**
   - Your job data appears as a normal Tableau data source
   - All fields are ready for immediate analysis
   - Refresh works like any other connection

---

## 📁 **File Guide**

```
📂 tableau-analytics-extensions-job-scraper/
├── 📄 secure_tableau_script.py                # Tableau Analytics Extension (production)
├── 📄 secure_vscode_script.py                 # VS Code testing version
├── 📄 config.py                               # 🔒 Secure credential loader
├── 📄 .env.template                           # 🔒 Template for your .env file
├── 📄 .env                                    # 🔒 Your private credentials (create from template)
├── 📄 requirements.txt                        # Python dependencies
├── 📄 .gitignore                              # 🔒 Protects sensitive files
├── 📄 LICENSE                                 # MIT License
├── 📄 README.md                               # This guide
└── 📂 examples/
    ├── 📄 sample_output.csv                   # Example of collected data
    └── 📄 tableau_dashboard.twbx               # Sample Tableau workbook
```

**🔒 Security Files:**
- **Use `secure_*.py`** versions (never the old hardcoded versions)
- **Create `.env`** from `.env.template` with your real API key
- **Never share** your `.env` file - it contains your private credentials

---

## ⚙️ **Configuration Guide**

### **🔒 Secure Configuration (Recommended)**

Set these in your `.env` file instead of modifying code:

```env
# API Credentials (Required)
JOB_API_KEY=your_jooble_api_key_here

# Search Parameters (Optional - modify to customize behavior)
DEFAULT_SEARCH_KEYWORDS=data analyst
DEFAULT_SEARCH_LOCATION=uk
DEFAULT_TARGET_JOBS=200
DEFAULT_MAX_PAGES=6
```

### **Popular Modifications**

| Goal | Change This in .env | Example |
|------|---------------------|---------|
| **Different job types** | `DEFAULT_SEARCH_KEYWORDS` | `data analyst`, `python developer` |
| **Other countries** | `DEFAULT_SEARCH_LOCATION` | `uk`, `ca`, `au`, `de` |
| **More job listings** | `DEFAULT_TARGET_JOBS`, `DEFAULT_MAX_PAGES` | `200`, `6` |
| **Faster execution** | `DEFAULT_TARGET_JOBS`, `DEFAULT_MAX_PAGES` | `60`, `2` |

### **Advanced Configuration**

For users comfortable with Python, you can modify the secure scripts:
- **API endpoints** (switch to different job sites)
- **Data processing logic** (custom field creation)
- **Geographic parsing** (handle international address formats)
- **Error handling** (custom diagnostic information)

---

## 🧪 **Testing Your Setup**

### **Test in VS Code First**
```bash
secure_vscode_script.py
```

**Expected Output:**
```
=== RUNNING SECURE JOB SCRAPER IN VS CODE ===
🔒 Using environment variables for API credentials
✅ API credentials loaded successfully!
🔍 Searching for: 'tableau' in 'us'
📊 Target: 120 jobs across max 4 pages
📄 Fetching page 1...
✅ Found 25 jobs on page 1
[...continues...]
SUCCESS: Found 120 jobs!
```

### **Test Minimal Analytics Extension**
Use this to verify your Tableau Analytics Extensions setup:

```python
import pandas as pd
from config import Config

try:
    Config.validate_required_credentials()
    test_data = {
        'status': ['SUCCESS'],
        'message': ['Credentials loaded successfully'],
        'api_key_status': ['Valid']
    }
    df = pd.DataFrame(test_data)
except ValueError as e:
    df = pd.DataFrame({'error': [str(e)]})

return df
```

---

## 📈 **Data Structure & Fields**

### **Output Fields**
Your Tableau data source will contain these fields:

| Field Name | Type | Description | Tableau Use |
|------------|------|-------------|-------------|
| `id` | String | Unique job identifier | Primary key for relationships |
| `title` | String | Job title | Dimension for filtering/grouping |
| `company` | String | Company name | Dimension for analysis |
| `location` | String | Original location from API | Reference field |
| `city` | String | **Parsed city name** | Geographic dimension |
| `state` | String | **Parsed state/region** | Geographic dimension |
| `snippet` | String | Job description preview | Text analysis |
| `salary` | String | Salary information | Analysis (if available) |
| `type` | String | Employment type | Dimension (Full-time, Contract, etc.) |
| `source` | String | Original job board | Dimension for source analysis |
| `link` | String | Direct job posting URL | Action/URL field |
| `updated` | String | Last update timestamp | Temporal analysis |

### **Enhanced Geographic Analysis**

The script automatically transforms:
- `"Seattle, WA"` → **City**: `"Seattle"`, **State**: `"WA"`
- `"New York, NY"` → **City**: `"New York"`, **State**: `"NY"`
- `"London"` → **City**: `"London"`, **State**: `"N/A"`

This enables:
✅ **State-level filtering** for regional analysis  
✅ **City mapping** with proper geographic roles  
✅ **Hierarchical geographic drilling** (State → City)  

---

## 🔧 **Troubleshooting Guide**

### **🔒 Security-Related Issues**

#### **"Missing API credentials" Error**
- **Cause**: `.env` file not found or `JOB_API_KEY` not set
- **Solution**: 
  1. Verify `.env` file exists in same directory as scripts
  2. Check `JOB_API_KEY=your_key` is in `.env` (no quotes, no spaces)
  3. Ensure `python-dotenv` is installed: `pip install python-dotenv`

#### **"Module not found: config" Error**
- **Cause**: `config.py` not in same directory as script
- **Solution**: Place `config.py` in same folder as your script files

### **Common Issues for Tableau Users**

#### **"Analytics extension script is invalid"**
- **Cause**: TabPy connection issue or script syntax error
- **Solution**: 
  1. Verify TabPy is running (`localhost:9004` in browser should show status)
  2. Test Analytics Extension connection in Tableau
  3. Test with VS Code version first to verify credentials

#### **"Table returned by analytics extension script cannot be empty"**
- **Cause**: Script ran but returned no data
- **Solution**: 
  1. Check your internet connection
  2. Try broader search terms in `.env` file
  3. Verify API key is working with VS Code test

#### **Script runs but shows diagnostic data instead of jobs**
- **This is actually good!** The script is working and telling you what went wrong
- **Check the "Issue" field** in the diagnostic data for specific guidance
- **Common fixes**: Update search keywords in `.env` file

---

## 🔒 **Security Best Practices**

### **✅ DO:**
- Use the `secure_*.py` versions of scripts
- Keep your `.env` file private and local
- Share `.env.template` with others
- Use environment variables for all sensitive data

### **❌ DON'T:**
- Commit `.env` file to version control
- Share your actual API key
- Put credentials back in script code
- Override `.gitignore` protections

### **🔄 For Existing Users:**
If you're upgrading from hardcoded credentials:
1. Use the new `secure_*.py` scripts
2. Create `.env` file with your API key
3. Stop using the old hardcoded versions
4. Your functionality remains exactly the same

---

## 🎓 **Learning Path for Tableau Users**

### **Level 1: Use As-Is**
- Set up secure credentials in `.env` file
- Use scripts without modifications
- Focus on Tableau visualization and analysis

### **Level 2: Parameter Customization**
- Modify search parameters in `.env` file
- Adjust data collection amounts
- Experiment with different job markets

### **Level 3: Code Adaptation**
- Use the VS Code testing version for development
- Modify data processing logic in secure scripts
- Add custom calculated fields during collection

### **Level 4: New APIs**
- Adapt the secure pattern for other APIs
- Build your own custom data connectors
- Combine multiple API calls in one script

---

## 💡 **Extension Ideas**

### **Immediate Enhancements**
- **Multiple job boards**: Combine Indeed, LinkedIn, Glassdoor results
- **Salary normalization**: Convert salary ranges to comparable numbers
- **Skills extraction**: Parse job descriptions for required skills
- **Company enrichment**: Add company size, industry, location data

### **Advanced Applications**
- **Market analysis**: Track job trends over time with scheduled refreshes
- **Geographic insights**: Salary differences by region
- **Skills gap analysis**: Compare required vs. available skills
- **Competition mapping**: Visualize job density by location

---

## 🤝 **Getting Help**

### **Support Process**
1. **Check troubleshooting section** above first
2. **Test with VS Code version** to isolate issues
3. **Review diagnostic data** if scripts run but show errors
4. **Check security setup** - ensure `.env` file is configured correctly
5. **Open an issue** with your diagnostic data output (never include real API keys)

### **Resources for Learning More**
- 📚 **Tableau Analytics Extensions**: [Official Documentation](https://help.tableau.com/current/server/en-us/config_r_tabpy.htm)
- 🐍 **TabPy Guide**: [GitHub Repository](https://github.com/tableau/TabPy)
- 🔒 **Environment Variables**: [Best Practices Guide](https://12factor.net/config)

---

## 📄 **License & Attribution**

This project is open source under the MIT License. See `LICENSE` file for details.

**Built for the Tableau community** - feel free to adapt, modify, and share your improvements!

---

## 🎬 **Video Tutorial**

📺 **Watch the ~10-minute tutorial**: [https://youtu.be/fODpiOnVmcg]

The updated video will cover:
- ✅ Secure credential setup with `.env` files
- ✅ Analytics Extensions configuration  
- ✅ Script integration and testing
- ✅ Building your first job market dashboard

---
