from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_socketio import SocketIO, emit
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SESSION_TYPE'] = 'filesystem'
socketio = SocketIO(app)

def init_db():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE,
                 password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 text TEXT,
                 username TEXT)''')
    conn.commit()
    conn.close()

def update_db():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    try:
        c.execute('''ALTER TABLE messages ADD COLUMN username TEXT''')
    except sqlite3.OperationalError:
        # This will fail if the column already exists
        pass
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('chat'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    if user:
        session['username'] = username
        return redirect(url_for('chat'))
    return 'Invalid username or password'

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        return 'Username already taken'
    conn.close()
    session['username'] = username
    return redirect(url_for('chat'))

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('chat.html', username=session['username'])

@app.route('/get_messages')
def get_messages():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("SELECT text, username FROM messages")
    messages = [{'text': row[0], 'username': row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(messages)

@socketio.on('message')
def handle_message(data):
    msg = data['msg']
    username = data['username']
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (text, username) VALUES (?, ?)", (msg, username))
    conn.commit()
    conn.close()
    emit('message', {'msg': msg, 'username': username}, broadcast=True, include_self=False)


    

if __name__ == '__main__':
    init_db()
    update_db()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
