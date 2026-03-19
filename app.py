from flask import Flask, request, jsonify
import sqlite3
import hashlib

app = Flask(__name__)

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

# Функция хеширования пароля
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Регистрация пользователя
@app.route('/register', methods=['POST'])
def register():
    data = request.json

    # Валидация входных данных
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'error': 'Не заполнены все поля'
        }), 400

    username = data['username'].strip()
    password = data['password']

    # Проверка длины пароля
    if len(password) < 6:
        return jsonify({
            'success': False,
            'error': 'Пароль должен содержать минимум 6 символов'
        }), 400

    password_hash = hash_password(password)

    try:
        conn = sqlite3.connect('blog.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                  (username, password_hash))
        user_id = c.lastrowid  # Получаем ID нового пользователя
        conn.commit()
        conn.close()
        return jsonify({
            'success': True,
            'message': 'Пользователь успешно зарегистрирован',
            'user_id': user_id,
            'username': username
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({
            'success': False,
            'error': 'Пользователь с таким именем уже существует'
        }), 409
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Произошла ошибка: {str(e)}'
        }), 500

# Вход пользователя
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    # Валидация входных данных
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'error': 'Не заполнены все поля'
        }), 400

    username = data['username'].strip()
    password = data['password']
    password_hash = hash_password(password)

    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
              (username, password_hash))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({
            'success': True,
            'message': 'Вход выполнен успешно',
            'user_id': user[0],
            'username': user[1]
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': 'Неверное имя пользователя или пароль'
        }), 401

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/post', methods=['POST'])
def create_post():
    data = request.json

    # Валидация входных данных
    if not data or 'user_id' not in data or 'title' not in data or 'content' not in data:
        return jsonify({
            'success': False,
            'error': 'Не заполнены все обязательные поля'
        }), 400

    user_id = data['user_id']
    title = data['title'].strip()
    content = data['content'].strip()
    tags = data.get('tags', '').strip()  # Опциональное поле
    visibility = data.get('visibility', 'public')  # По умолчанию — публичный

    # Дополнительная валидация
    if len(title) < 3:
        return jsonify({
            'success': False,
            'error': 'Заголовок должен содержать минимум 3 символа'
        }), 400
    if len(content) < 10:
        return jsonify({
            'success': False,
            'error': 'Содержание поста должно содержать минимум 10 символов'
        }), 400

    try:
        conn = sqlite3.connect('blog.db')
        c = conn.cursor()
        c.execute("""
            INSERT INTO posts (user_id, title, content, tags, visibility)
            VALUES (?, ?, ?, ?, ?)
        "", (user_id, title, content, tags, visibility))
        post_id = c.lastrowid  # Получаем ID созданного поста
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Пост успешно создан',
            'post_id': post_id,
            'title': title
        }), 201
    except sqlite3.Error as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка базы данных: {str(e)}'
        }), 500
def create_subscriptions_table():
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                 (follower_id INTEGER,
                  following_id INTEGER,
                  PRIMARY KEY (follower_id, following_id),
                  FOREIGN KEY (follower_id) REFERENCES users (id),
                  FOREIGN KEY (following_id) REFERENCES users (id))''')
    conn.commit()
    conn.close()

create_subscriptions_table()
@app.route('/follow', methods=['POST'])
def follow_user():
    data = request.json

    # Валидация входных данных
    if not data or 'follower_id' not in data or 'following_id' not in data:
        return jsonify({
            'success': False,
            'error': 'Не заполнены все обязательные поля'
        }), 400

    follower_id = data['follower_id']
    following_id = data['following_id']

    # Проверка, что пользователь не пытается подписаться на себя
    if follower_id == following_id:
        return jsonify({
            'success': False,
            'error': 'Нельзя подписаться на самого себя'
        }), 400

    try:
        conn = sqlite3.connect('blog.db')
        c = conn.cursor()
        # Проверяем, не подписан ли уже пользователь
        c.execute("SELECT 1 FROM subscriptions WHERE follower_id = ? AND following_id = ?",
                  (follower_id, following_id))
        if c.fetchone():
            return jsonify({
                'success': False,
                'error': 'Вы уже подписаны на этого пользователя'
            }), 409

        # Добавляем подписку
        c.execute("INSERT INTO subscriptions (follower_id, following_id) VALUES (?, ?)",
                  (follower_id, following_id))
        conn.commit()
        conn.close()
        return jsonify({
            'success': True,
            'message': 'Подписка оформлена успешно'
        }), 201
    except sqlite3.Error as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка базы данных: {str(e)}'
        }), 500
@app.route('/unfollow', methods=['POST'])
def unfollow_user():
    data = request.json

    if not data or 'follower_id' not in data or 'following_id' not in data:
        return jsonify({
            'success': False,
            'error': 'Не заполнены все обязательные поля'
        }), 400

    follower_id = data['follower_id']
    following_id = data['following_id']

    try:
        conn = sqlite3.connect('blog.db')
        c = conn.cursor()
        c.execute("DELETE FROM subscriptions WHERE follower_id = ? AND following_id = ?",
                  (follower_id, following_id))
        if c.rowcount == 0:  # Если ни одной строки не удалено
            return jsonify({
                'success': False,
                'error': 'Подписка не найдена'
            }), 404
        conn.commit()
        conn.close()
        return jsonify({
            'success': True,
            'message': 'Отписка выполнена успешно'
        }), 200
    except sqlite3.Error as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка базы данных: {str(e)}'
        }), 500
@app.route('/user/<int:user_id>/subscriptions', methods=['GET'])
def get_user_subscriptions(user_id):
    """Получает список пользователей, на которых подписан user_id"""
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute("""
        SELECT u.id, u.username
        FROM users u
        JOIN subscriptions s ON u.id = s.following_id
        WHERE s.follower_id = ?
    "", (user_id,))
    subscriptions = c.fetchall()
    conn.close()
    result = [{'id': sub[0], 'username': sub[1]} for sub in subscriptions]
    return jsonify(result)

@app.route('/user/<int:user_id>/followers', methods=['GET'])
def get_user_followers(user_id):
    """Получает список подписчиков user_id"""
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute("""
        SELECT u.id, u.username
        FROM users u
        JOIN subscriptions s ON u.id = s.follower_id
        WHERE s.following_id = ?
    "", (user_id,))
    followers = c.fetchall()
    conn.close()
    result = [{'id': fol[0], 'username': fol[1]} for fol in followers]
    return jsonify(result)

