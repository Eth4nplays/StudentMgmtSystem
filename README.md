# Student Management System
A web application for managing after-school activities with different user roles using Firebase and Python with Streamlit

# Setting up
## Requirements
You must have installed:
- Python 3
- Git

Dependencies for Python:
- extra-streamlit-components
- streamlit
- firebase-admin

## Cloning the repo
1) Clone the repo
```bash
git clone https://github.com/Eth4nplays/StudentMgmtSystem.git
```
2) Enter the repo folder
```bash
cd StudentMgmtSystem
```
## Creating Fireabse project
1) Create a Firebase project on https://console.firebase.google.com/
2) Get API key by creating a web app within the console
3) Get database URL by creating a Firebase Realtime Database
4) Paste these two into `.streamlit/secrets.toml` as:
```toml
[firebase]
api_key = "apiKeyHere67676767676767"
database_url = "https://your-project-default-rtdb.firebaseio.com"
```
5) Generate private key of Python Firebase Admin SDK service account from the "Service Accounts" tab of project settings
6) Paste contents into the `.streamlit/secrets.toml` as:
```toml
[firebase_admin]
"type": "service_account",
"project_id": "amazingBestProject",
"private_key_id": "676767abcd67privatekeyhere6767",

...
```
## Hosting the application
1) Running the program
Run the following:
```bash
python -m streamlit run StudentMgmtSystem
```
