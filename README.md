# secure-cloud-system


Secure File Sharing Web App is a Flask-based web application that allows users to securely upload, encrypt, and share files using Dropbox integration.

## Features

- **Encryption:** Files are encrypted using the Fernet symmetric encryption algorithm.
- **Dropbox Integration:** Integration with Dropbox for secure file storage and retrieval.
- **Email Notification:** Users can send email notifications with decryption keys and file links.

## Prerequisites

Before running the application, ensure you have the following:

- Python 3.x installed.
- Required Python packages installed. You can install them using:

Configuration:

Dropbox Access Token:
Replace 'YOUR_DROPBOX_ACCESS_TOKEN' in app.py with your actual Dropbox access token.

Email Configuration:
Replace the email-related placeholders in app.py with your actual email credentials.

Usage:
Run the Flask application:

bash
Copy code
python app.py
Open your browser and navigate to http://127.0.0.1:5000/ to access the application.

Follow the on-screen instructions to encrypt, upload, and share files securely.


Important Notes:

Security Warning: Ensure to keep sensitive information such as access tokens and encryption keys confidential. Do not expose them in public repositories.
