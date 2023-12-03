from flask import Flask, render_template, request, send_file
from cryptography.fernet import Fernet
import os

app = Flask(__name__)

def decrypt_file(uploaded_file, key):
    try:
        encrypted_data = uploaded_file.read()

        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)

        original_file_name = uploaded_file.filename.replace('_encrypted', '_decrypted')

        with open(original_file_name, 'wb') as file:
            file.write(decrypted_data)

        return original_file_name
    except Exception as e:
        return f"An error occurred during decryption: {str(e)}"

@app.route('/')
def index():
    return render_template('indexd.html')

@app.route('/decrypt_and_download', methods=['POST'])
def decrypt_and_download():
    uploaded_file = request.files.get('uploaded_file')
    key = request.form.get('key')

    if not uploaded_file or not key:
        return "Invalid request. Please provide the encrypted file and decryption key."

    decrypted_file_path = decrypt_file(uploaded_file, key)

    if decrypted_file_path.startswith("An error occurred during decryption"):
        return decrypted_file_path

    return send_file(decrypted_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
