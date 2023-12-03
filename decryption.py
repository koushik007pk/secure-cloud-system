import tkinter as tk
from tkinter import filedialog, Entry, Button, Label
from cryptography.fernet import Fernet


def decrypt_file():
    key = key_entry.get()
    encrypted_file_path = file_entry.get()

    try:
        with open(encrypted_file_path, 'rb') as file:
            encrypted_data = file.read()

        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)

        original_file_name = encrypted_file_path.replace('_encrypted', '_decrypted')

        with open(original_file_name, 'wb') as file:
            file.write(decrypted_data)

        result_label.config(text=f"Decryption complete. Decrypted file saved as {original_file_name}")
    except Exception as e:
        result_label.config(text=f"An error occurred during decryption: {str(e)}")


def browse_file():
    file_path = filedialog.askopenfilename(title="Select the Encrypted File")
    file_entry.delete(0, tk.END)
    file_entry.insert(0, file_path)


root = tk.Tk()
root.title("File Decryption")

key_label = Label(root, text="Decryption Key:")
key_label.pack()

key_entry = Entry(root, show="*")
key_entry.pack()

file_label = Label(root, text="Encrypted File:")
file_label.pack()

file_entry = Entry(root)
file_entry.pack()

browse_button = Button(root, text="Browse", command=browse_file)
browse_button.pack()

decrypt_button = Button(root, text="Decrypt", command=decrypt_file)
decrypt_button.pack()

result_label = Label(root, text="")
result_label.pack()

root.mainloop()
