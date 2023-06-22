from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import hashlib
from cryptography.fernet import Fernet
import requests

app = Flask(__name__)
app.config['MYSQL_HOST'] = '#'
app.config['MYSQL_USER'] = '#'
app.config['MYSQL_PASSWORD'] = '#'
app.config['MYSQL_DB'] = '#'

mysql = MySQL(app)

key = b'owJrH7EVzrrzz0i0bxbNTdKcvg6-V-Lbq00gch6ABqQ='  # Przykładowy klucz używany do szyfrowania
cipher_suite = Fernet(key)

def get_random_animal_image():
    api_url = "https://some-random-api.com/animal/cat" 
    response = requests.get(api_url).json()
    animal_image = response["image"]
    return animal_image

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM tasks')
    tasks = cur.fetchall()
    cur.close()

    decrypted_tasks = []
    for task in tasks:
        task_id = task[0]
        title = task[1]
        encrypted_description = task[2]
        ip_address = task[3]
        animal_image = task[4]

        decrypted_description = decrypt_description(encrypted_description)

        decrypted_tasks.append((task_id, title, decrypted_description, ip_address, animal_image))

    return render_template('index.html', tasks=decrypted_tasks)

def encrypt_description(description):
    encrypted_text = cipher_suite.encrypt(description.encode())
    return encrypted_text

def decrypt_description(encrypted_text):
    decrypted_text = cipher_suite.decrypt(encrypted_text).decode()
    return decrypted_text

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form['title']
    description = request.form['description']
    ip_address = request.remote_addr  
    animal_image = get_random_animal_image()  

    encrypted_description = encrypt_description(description)

    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO tasks (title, description, ip_address, animal_image) VALUES (%s, %s, %s, %s)', (title, encrypted_description, ip_address, animal_image))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM tasks WHERE id = %s', (task_id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
