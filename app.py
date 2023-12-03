from flask import Flask, render_template, session, request
import os
from cryptography.fernet import Fernet
import dropbox
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Replace 'YOUR_DROPBOX_ACCESS_TOKEN' with your actual Dropbox access token
access_token = 'sl.BqZ72JdefZVDIKFZL7aifqIEgKO08QlnX2EQaAYZRpg8j3bLMs4p9Uh6bGOdcEzPBFWfSUQwU6q6jiorsqWfLTQlE1et6rm3jcRdfRUKfNDwHPSrK1-Let-IvZ_-UgYrTC-tzK7rpf7iYcOSkmrxlK0'
dbx = dropbox.Dropbox(access_token)

def generate_key():
    return Fernet.generate_key()

def initialize_dropbox_client(access_token):
    return dropbox.Dropbox(access_token)

def encrypt_and_upload(file, fernet, dbx):
    if not file:
        return "No file selected."

    try:
        file_data = file.read()
        encrypted_data = fernet.encrypt(file_data)

        _, original_extension = os.path.splitext(file.filename)
        encrypted_file = os.path.splitext(file.filename)[0] + '_encrypted' + original_extension

        with open(encrypted_file, 'wb') as f:
            f.write(encrypted_data)

        uploaded_file_path = '/' + encrypted_file
        with open(encrypted_file, 'rb') as f:
            dbx.files_upload(f.read(), uploaded_file_path, mode=dropbox.files.WriteMode("add"))

        # Store the uploaded file path in the session
        session['uploaded_file_path'] = uploaded_file_path

        return f'File {encrypted_file} uploaded to Dropbox.'
    except Exception as e:
        return f"An error occurred during encryption: {str(e)}"

def decrypt_and_download(fernet, dbx):
    try:
        # Retrieve the uploaded file path from the session
        uploaded_file_path = session.get('uploaded_file_path')
        if not uploaded_file_path:
            return "No file uploaded for decryption."

        # Get the user's home directory
        home_dir = os.path.expanduser("~")

        # Specify the local path for the decrypted file in the "Downloads" folder
        downloads_folder = os.path.join(home_dir, "Downloads")
        decrypted_file = os.path.join(downloads_folder, os.path.splitext(os.path.basename(uploaded_file_path))[0] + '_decrypted' + os.path.splitext(uploaded_file_path)[1])

        # Download the encrypted file from Dropbox
        dbx.files_download_to_file(decrypted_file, uploaded_file_path)

        # Decrypt the downloaded file
        with open(decrypted_file, 'rb') as f:
            encrypted_data = f.read()

        decrypted_data = fernet.decrypt(encrypted_data)

        # Specify the local path for the decrypted file
        decrypted_file = os.path.splitext(decrypted_file)[0] + '_decrypted' + os.path.splitext(decrypted_file)[1]

        with open(decrypted_file, 'wb') as f:
            f.write(decrypted_data)

        return f'Decrypted file saved as {decrypted_file}'
    except Exception as e:
        return f"An error occurred during decryption: {str(e)}"

def send_email(recipient_email, encryption_key, file_link):
    try:
        # Replace with your email credentials
        smtp_server = 'smtp-mail.outlook.com'
        smtp_port = 587  # Port for secure TLS
        smtp_username = 'koushikpraneeth0@outlook.com'  # Replace with your Outlook/Hotmail email address
        smtp_password = '07pranithpK'  # Replace with your email password

        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = recipient_email
        msg['Subject'] = "Shared File and Key"

        # Add the message body
        msg.attach(MIMEText(f"Here is the decryption key: {encryption_key}\nHere is the link to the file: {file_link}", 'plain'))

        # Create a secure connection to the email server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        # Log in to the email server
        server.login(smtp_username, smtp_password)

        # Send the email
        server.sendmail(smtp_username, recipient_email, msg.as_string())

        # Quit the server
        server.quit()

        return "Email sent successfully."
    except Exception as e:
        return f"An error occurred while sending the email: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt_and_upload', methods=['POST'])
def encrypt_and_upload_web():
    if 'encryption_key' not in session:
        session['encryption_key'] = generate_key()

    access_token = 'sl.BqZ72JdefZVDIKFZL7aifqIEgKO08QlnX2EQaAYZRpg8j3bLMs4p9Uh6bGOdcEzPBFWfSUQwU6q6jiorsqWfLTQlE1et6rm3jcRdfRUKfNDwHPSrK1-Let-IvZ_-UgYrTC-tzK7rpf7iYcOSkmrxlK0'
    dbx = initialize_dropbox_client(access_token)
    fernet = Fernet(session['encryption_key'])

    file = request.files['file']

    result = encrypt_and_upload(file, fernet, dbx)

    return render_template('result.html', message=result)

@app.route('/decrypt_and_download', methods=['POST'])
def decrypt_and_download_web():
    if 'encryption_key' not in session:
        return "Encryption key not found in session."

    access_token = 'sl.BqZ72JdefZVDIKFZL7aifqIEgKO08QlnX2EQaAYZRpg8j3bLMs4p9Uh6bGOdcEzPBFWfSUQwU6q6jiorsqWfLTQlE1et6rm3jcRdfRUKfNDwHPSrK1-Let-IvZ_-UgYrTC-tzK7rpf7iYcOSkmrxlK0k.'
    dbx = initialize_dropbox_client(access_token)
    fernet = Fernet(session['encryption_key'])

    result = decrypt_and_download(fernet, dbx)

    return render_template('result.html', message=result)

@app.route('/send_email', methods=['POST'])
def send_email_web():
    recipient_email = request.form['recipient_email']
    encryption_key = session.get('encryption_key')
    file_link = session.get('uploaded_file_path')

    if not recipient_email or not encryption_key or not file_link:
        return "Recipient's email, encryption key, or file link not found."

    email_result = send_email(recipient_email, encryption_key.decode(), file_link)

    return render_template('result.html', message=email_result)

if __name__ == '__main__':
    app.run(debug=True)
