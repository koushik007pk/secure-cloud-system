import mimetypes
import threading
import os
import tkinter as tk
from tkinter import messagebox, filedialog, Entry, Label, Button, StringVar
from cryptography.fernet import Fernet
import dropbox
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Create a variable to store the currently running thread
current_thread = None

# Global variables for the Fernet key and Dropbox client
fernet = None
dbx = None




# Global variable for the uploaded file path
uploaded_file_path = None

# Function to generate a Fernet key
def generate_key():
    return Fernet.generate_key()

# Function to initialize the Dropbox client
def initialize_dropbox_client(access_token):
    global dbx
    dbx = dropbox.Dropbox(access_token)

# Function to handle encryption and uploading
def encrypt_and_upload():
    global current_thread, fernet

    if current_thread and current_thread.is_alive():
        messagebox.showinfo("Task in Progress", "A task is already running.")
        return

    current_thread = threading.Thread(target=perform_encryption_and_upload)
    current_thread.start()

def update_gui_after_task_complete():
    # Update the GUI or show a message when the task is complete
    if current_thread.is_alive():
        root.after(100, update_gui_after_task_complete)
    else:
        messagebox.showinfo("Task Complete", "Encryption and upload completed.")

def perform_encryption_and_upload():
    global fernet, uploaded_file_path, encryption_key

    # Generate a new Fernet key
    encryption_key = generate_key()
    fernet = Fernet(encryption_key)

    # Prompt the user to select a file for encryption
    file_to_encrypt = filedialog.askopenfilename(title="Select a file to encrypt")
    if not file_to_encrypt:
        return  # User canceled file selection

    try:
        with open(file_to_encrypt, 'rb') as f:
            file_data = f.read()

        encrypted_data = fernet.encrypt(file_data)

        # Get the original file extension
        _, original_extension = os.path.splitext(file_to_encrypt)

        # Specify the local path for the encrypted file
        encrypted_file = os.path.splitext(os.path.basename(file_to_encrypt))[0] + '_encrypted' + original_extension

        with open(encrypted_file, 'wb') as f:
            f.write(encrypted_data)

        # Upload to Dropbox
        uploaded_file_path = '/' + encrypted_file
        with open(encrypted_file, 'rb') as f:
            dbx.files_upload(f.read(), uploaded_file_path, mode=dropbox.files.WriteMode("add"))

        # Generate a shared link for the uploaded file
        shared_link = dbx.sharing_create_shared_link(path=uploaded_file_path)
        shared_link_url = shared_link.url

        # Ask if you want to upload to Dropbox
        upload_choice = messagebox.askyesno("Upload to Dropbox", "Do you want to upload the encrypted file to Dropbox?")

        if upload_choice:
            # Display the shared link to the user
            messagebox.showinfo("Upload Complete", f'File {encrypted_file} uploaded to Dropbox. Shared Link: {shared_link_url}')
        else:
            messagebox.showinfo("Encryption Complete", f'Encryption complete. File {encrypted_file} not uploaded to Dropbox.')

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

        # Update the GUI when the task is complete
        root.after(100, update_gui_after_task_complete)


# Function to handle decryption and downloading
def decrypt_and_download():
    global current_thread, fernet

    if current_thread and current_thread.is_alive():
        messagebox.showinfo("Task in Progress", "A task is already running.")
        return

    current_thread = threading.Thread(target=perform_decryption_and_download)
    current_thread.start()

def perform_decryption_and_download():
    global fernet, uploaded_file_path

    # Ask for downloading from Dropbox
    download_choice = messagebox.askyesno("Download from Dropbox", "Do you want to download the most recently uploaded encrypted file from Dropbox?")

    if download_choice:
        try:
            if not uploaded_file_path:
                messagebox.showinfo("No Uploaded File", "No file has been uploaded to Dropbox.")
                return

            # Specify the local path where you want to save the downloaded file
            downloaded_file_path = filedialog.asksaveasfilename(title="Save Decrypted File")

            if not downloaded_file_path:
                return  # User canceled file save

            # Download the most recently uploaded encrypted file from Dropbox
            try:
                dbx.files_download_to_file(downloaded_file_path, uploaded_file_path)
            except dropbox.exceptions.ApiError as api_error:
                messagebox.showerror("Dropbox API Error", f"Dropbox API error: {str(api_error)}")
                return

            # Log a success message
            print("File downloaded successfully")

            # Extract the original extension from the uploaded file path
            _, original_extension = os.path.splitext(uploaded_file_path)

            # Construct the local path for the decrypted file with the correct file extension
            decrypted_filename = os.path.splitext(downloaded_file_path)[0] + '_decrypted' + original_extension

            with open(downloaded_file_path, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = fernet.decrypt(encrypted_data)

            with open(decrypted_filename, 'wb') as f:
                f.write(decrypted_data)

            messagebox.showinfo("Download Complete", f'Decrypted file saved as {decrypted_filename}')
        except Exception as e:
            messagebox.showerror("Download Error", f"An error occurred during the download or decryption: {str(e)}")
    else:
        messagebox.showinfo("Download Skipped", "Decryption and download skipped.")

        # Update the GUI when the task is complete
        root.after(100, update_gui_after_task_complete)

def send_email():
    recipient_email = recipient_email_var.get()
    if not recipient_email:
        messagebox.showerror("Error", "Recipient's email is required.")
        return

    if not uploaded_file_path:
        messagebox.showerror("Error", "No file has been uploaded to Dropbox.")
        return

    # Create a secure connection to the email server and send the email
    try:
        # SMTP server and port for Outlook/Hotmail
        smtp_server = 'smtp-mail.outlook.com'
        smtp_port = 587  # Port for secure TLS
        smtp_username = 'koushikpraneeth0@outlook.com'  # Replace with your Outlook/Hotmail email address
        smtp_password = '07pranithpK'  # Replace with your email password

        # Generate a shared link for the uploaded file
        shared_link = dbx.sharing_create_shared_link(path=uploaded_file_path)
        shared_link_url = shared_link.url

        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = recipient_email
        msg['Subject'] = "Shared File and Key"

        # Add the message body
        msg.attach(
            MIMEText(f"Here is the decryption key: {encryption_key.decode()}\nHere is the link to the file: {shared_link_url}", 'plain'))

        # Create a secure connection to the email server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        # Log in to the email server
        server.login(smtp_username, smtp_password)

        # Send the email
        server.sendmail(smtp_username, recipient_email, msg.as_string())

        # Quit the server
        server.quit()

        messagebox.showinfo("Email Sent", f"Email sent to {recipient_email} with the key and file link.")
    except Exception as e:
        messagebox.showerror("Email Error", f"An error occurred while sending the email: {str(e)}")


# Replace 'YOUR_DROPBOX_ACCESS_TOKEN' with your actual Dropbox access token
access_token = 'sl.BpyUSEPeXHIueZ7QsFGAWLfklk7puWrgDnEAkTqYT92J5ZuO6WvKC9FuWbvTdUMGCPneLSNaLAqZV9cqBAK_7fgcA7iqEJQGAmq4p7TvAS1RMG85BGu4yVfUXK8nGr9I44WYCRm_i7uWYjWwTUMkKjk'
initialize_dropbox_client(access_token)

# Create the main window
root = tk.Tk()
root.title("File Decryption and Download")

# Create a button for encryption and uploading
encrypt_button = tk.Button(root, text="Encrypt and Upload", command=encrypt_and_upload)
encrypt_button.pack()

# Create a button for decryption and downloading
download_button = tk.Button(root, text="Decrypt and Download", command=decrypt_and_download)
download_button.pack()

# Create a button for sharing the file and key via email
share_button = tk.Button(root, text="Share via Email", command=send_email)
share_button.pack()

# Create an Entry widget for entering the recipient's email
recipient_email_var = StringVar()
recipient_email_entry = Entry(root, textvariable=recipient_email_var)
recipient_email_label = Label(root, text="Recipient's Email:")
recipient_email_label.pack()
recipient_email_entry.pack()

# Start the Tkinter main loop
root.mainloop()
