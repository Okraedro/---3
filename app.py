from flask import Flask, request, jsonify, render_template
import sqlite3
import hashlib

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    # Пользователи
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password_hash TEXT)''')
    # Посты
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  title TEXT,
                  content TEXT,
                  tags TEXT,
                  visibility TEXT,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    # Подписки
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                 (follower_id INTEGER,
                  following_id INTEGER,
                  PRIMARY KEY (follower_id, following_id),
                  FOREIGN KEY (follower_id) REFERENCES users (id),
                  FOREIGN KEY (following_id) REFERENCES users (id))''')
    # Комментарии
    c.execute('''CREATE TABLE IF NOT EXISTS comments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  post_id INTEGER,
                  user_id INTEGER,
                  content TEXT,
                  FOREIGN KEY (post_id) REFERENCES posts (id),
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    conn.commit()
    conn.close()

init_db()
