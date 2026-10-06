<img width="280.4" height="204" alt="Student Management System by B.E. Water" src="https://github.com/user-attachments/assets/d2ed9b9f-3817-4843-b9a8-884a561102e9" /> 

# Student Management System
A web application for managing after-school activities with different user roles using Firebase and Python with Streamlit

# Features:
- Account management
- Classes
   - Task management
   - Reports
   - Attendance
   - Schedule
- Announcements & Inbox

# Setting up
## Requirements
You must have installed:
- Python 3
- Git

## Cloning the repo
1) Clone the repo
```bash
git clone https://github.com/Eth4nplays/StudentMgmtSystem.git
```
2) Enter the repo folder
```bash
cd StudentMgmtSystem
```

## Installing dependencies
1) Run the following:
```bash
python -m pip install -r requirements.txt
```

## Creating Firebase project
> [!NOTE]
> If you have been provided the secrets.toml file (located in .streamlit/config.toml), you may ignore this and skip to the next steps.
1) Create a Firebase project on https://console.firebase.google.com/
2) Set up Authentication
   - Select from the sidebar: Security > Authentication
   - Enable authentication in the project
   - Add the "Email/Password" provider for authentication
3) Set up Realtime Database
   - Select from the sidebar: Databases & Storage > Realtime Database
   - Enable realtime database with the **United States (us-central1)** server selected
   - Select the **test mode** security rule *(we selected test mode for demonstration and debugging purposes only. for deployment, proper rules should be configured)*
4) Get API key by creating a web app within the console
   - Select from the sidebar: Settings > General
   - Scroll down to the "Your Apps" section
   - Click on "Add App" > "Web App"
   - Copy the apiKey and databaseURL somewhere, you'll need it later.

5) Generate private key of Python Firebase Admin SDK service account
   - Select from the sidebar: Settings > Service Accounts
   - Select the "Firebase Admin SDK" tab and select "Generate new private key"
   - Download the JSON. You'll need it later.

6) Paste contents into the `.streamlit/secrets.toml` in this format:
```toml
# Paste the apiKey and databaseURL you copied into the fields below.
[firebase]
api_key = "API_KEY_HERE"
database_url = "DATABASE_URL_HERE"

# Paste each of the contents from the JSON you downloaded into the fields below.
[firebase_admin]
"type"= "service_account"
"project_id"= "PROJECT_ID_HERE"
"private_key_id"= "PRIVATE_KEY_ID_HERE"
"private_key"= "PRIVATE_KEY_HERE"
"client_email"= "CLIENT_EMAIL_HERE"
"client_id"= "CLIENT_ID_HERE"
"auth_uri"= "AUTH_URI_HERE"
"token_uri"= "TOKEN_URI_HERE"
"auth_provider_x509_cert_url"= "AUTH_PROV_CERT_URL_HERE"
"client_x509_cert_url"= "CLIENT_CERT_URL_HERE"
"universe_domain"= "UNIV_DOMAIN_HERE"
```

## Creating MongoDB Database
> [!NOTE]
> Once again, if you have been provided the secrets.toml file (located in .streamlit/config.toml), you may ignore this and skip to the next steps.
1) Create an account in MongoDB Atlas on https://cloud.mongodb.com/
2) Create a project in MongoDB Atlas
3) Create a cluster in your project *(you can use the free plan for now)*
4) Copy the password for the database user to somewhere, you'll need it later
5) Enter the cluster, select "Connect" > "Drivers and Client Libraries"
6) Select "Python" as the language and "PyMongo (Synchronous)" as Client Library
7) Copy the connection string, replace the `<db_password>` inside with the password you copied
8) Paste content into the `.streamlit/secrets.toml` in this format:
```toml
# You can paste this below the Firebase secrets
[mongodb]
uri = "CONNECTION_STRING_HERE"
```

## Hosting the application
1) Running the program
Run the following:
```bash
python -m streamlit run
```
2) Streamlit will provide a URL. Open it in your browser to start using the app.