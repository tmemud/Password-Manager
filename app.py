# app.py

from flask import Flask, render_template, request, redirect, url_for
from cryptography.fernet import Fernet
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Generate a key for encryption/decryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Create database if not exists
conn = sqlite3.connect('passwords.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS passwords
             (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
conn.commit()
conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Authenticate user (e.g., check against a database)
        # If authentication successful, redirect to password manager page
        return redirect(url_for('password_manager'))
    return redirect(url_for('index'))

@app.route('/password-manager')
def password_manager():
    # Retrieve and decrypt passwords from the database
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute('SELECT * FROM passwords')
    passwords = c.fetchall()
    decrypted_passwords = [(row[0], row[1], cipher_suite.decrypt(row[2].encode()).decode()) for row in passwords]
    conn.close()
    return render_template('password_manager.html', passwords=decrypted_passwords)

@app.route('/add-password', methods=['POST'])
def add_password():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Encrypt password
        encrypted_password = cipher_suite.encrypt(password.encode()).decode()
        # Insert encrypted password into the database
        conn = sqlite3.connect('passwords.db')
        c = conn.cursor()
        c.execute('INSERT INTO passwords (username, password) VALUES (?, ?)', (username, encrypted_password))
        conn.commit()
        conn.close()
        return redirect(url_for('password_manager'))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
