<img width="280.4" height="204" alt="Student Management System by B.E. Water" src="https://github.com/user-attachments/assets/d2ed9b9f-3817-4843-b9a8-884a561102e9" /> 

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

This can be automatically imported by running `pip install -r requirements.txt`

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
2) Set up Authentication and Realtime Database<img width="800" height="363" alt="image" src="https://github.com/user-attachments/assets/2ab175b1-b1f5-41c6-95e8-653784a76fa2" /> 

3) Get API key by creating a web app within the console<img width="656" height="167" alt="image" src="https://github.com/user-attachments/assets/4d3aa41c-ef94-4736-b274-df571c6d9633" />
<img width="466" height="399" alt="image" src="https://github.com/user-attachments/assets/e0d6c39d-4d52-4023-9b22-48e88e651548" />

4) Generate private key of Python Firebase Admin SDK service account from the "Service Accounts" tab of project settings
   <img width="1021" height="728" alt="image" src="https://github.com/user-attachments/assets/e0293732-f92c-4a2d-a43c-c020345558fd" />

5) Paste contents into the `.streamlit/secrets.toml` in this format:
```toml
[firebase]
api_key = "API_KEY_HERE"
database_url = "DATABASE_URL_HERE"

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

## Hosting the application
1) Running the program
Run the following:
```bash
python -m streamlit run
```
