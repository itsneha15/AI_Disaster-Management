Create README.txt and write:

================================================
AI DISASTER RECOVERY SYSTEM - SETUP GUIDE
================================================

STEP 1 - Install Python
Download Python 3.11 from python.org
Check "Add to PATH" during install

STEP 2 - Install Libraries
Open PowerShell as Administrator
Run: pip install flask psutil watchdog
     scikit-learn lightgbm joblib
     pandas numpy schedule
     google-auth google-auth-oauthlib
     google-auth-httplib2
     google-api-python-client
     msal dropbox

STEP 3 - Setup Google Drive
1. Go to console.cloud.google.com
2. Create project
3. Enable Google Drive API
4. Create OAuth credentials
5. Download as credentials.json
6. Put in project root folder

STEP 4 - Setup Dropbox
1. Go to dropbox.com/developers
2. Create app
3. Generate access token
4. Paste in config.py

STEP 5 - Setup OneDrive
1. Go to portal.azure.com
2. Register new app
3. Copy client ID
4. Paste in config.py

STEP 6 - Rename config file
Rename config_template.py
to config.py

STEP 7 - Run Project
Open PowerShell
cd C:\AI_Disaster_Recovery
python app.py

Open browser:
http://127.0.0.1:5000
Login: admin / password
================================================