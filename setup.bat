@echo off
echo Installing all libraries...
pip install flask
pip install psutil
pip install watchdog
pip install scikit-learn
pip install lightgbm
pip install joblib
pip install pandas
pip install numpy
pip install schedule
pip install google-auth
pip install google-auth-oauthlib
pip install google-auth-httplib2
pip install google-api-python-client
pip install msal
pip install dropbox
pip install pefile
echo.
echo All libraries installed!
echo.
echo Now do these steps:
echo 1. Setup Google Drive credentials
echo 2. Setup Dropbox token
echo 3. Setup OneDrive client ID
echo 4. Fill in config.py
echo 5. Run: python app.py
pause