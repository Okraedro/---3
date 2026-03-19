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
    c.execute('''CREATE TABLE IF NOT EXISTS access_requests
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              post_id INTEGER,
              author_id INTEGER,
              requester_id INTEGER,
              status TEXT DEFAULT 'pending',
              requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (post_id) REFERENCES posts (id),
              FOREIGN KEY (author_id) REFERENCES users (id),
              FOREIGN KEY (requester_id) REFERENCES users (id))''')
c.execute('''CREATE TABLE IF NOT EXISTS granted_access
             (post_id INTEGER,
              user_id INTEGER,
              granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (post_id, user_id),
              FOREIGN KEY (post_id) REFERENCES posts (id),
              FOREIGN KEY (user_id) REFERENCES users (id))''')

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

@app.route('/feed/<int:user_id>', methods=['GET'])
def get_user_feed(user_id):
    """
    Возвращает посты пользователей, на которых подписан user_id.
    Включает только публичные посты.
    """
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()

    # Получаем ID пользователей, на которых подписан текущий пользователь
    c.execute("""
        SELECT following_id
        FROM subscriptions
        WHERE follower_id = ?
    "", (user_id,))
    following_ids = [row[0] for row in c.fetchall()]

    if not following_ids:
        # Если нет подписок, возвращаем пустой список
        conn.close()
        return jsonify([])

    # Формируем строку с плейсхолдерами для IN-запроса
    placeholders = ','.join('?' * len(following_ids))

    # Получаем посты от пользователей, на которых подписан пользователь
    query = f"""
        SELECT
            p.id,
            p.user_id,
            p.title,
            p.content,
            p.tags,
            p.visibility,
            u.username,
            p.created_at
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.user_id IN ({placeholders})
          AND p.visibility = 'public'
        ORDER BY p.created_at DESC, p.id DESC
    """

    c.execute(query, following_ids)
    posts = c.fetchall()
    conn.close()

    # Форматируем результат
    result = []
    for post in posts:
        result.append({
            'id': post[0],
            'user_id': post[1],
            'title': post[2],
            'content': post[3],
            'tags': post[4],
            'visibility': post[5],
            'username': post[6],
            'created_at': post[7] if post[7] else 'Неизвестно'
        })

    return jsonify(result)
@app.route('/users', methods=['GET'])
def get_all_users():
    """Возвращает список всех пользователей (для поиска и подписки)"""
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute("SELECT id, username FROM users ORDER BY username")
    users = c.fetchall()
    conn.close()

    result = [{'id': user[0], 'username': user[1]} for user in users]
    return jsonify(result)
@app.route('/posts/public', methods=['GET'])
def get_public_posts():
    """
    Возвращает все публичные посты с информацией об авторах.
    Сортирует по дате создания (новые сверху).
    """
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()

    c.execute("""
        SELECT
            p.id,
            p.user_id,
            p.title,
            p.content,
            p.tags,
            p.visibility,
            u.username,
            p.created_at
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.visibility = 'public'
        ORDER BY p.created_at DESC, p.id DESC
    "")

    posts = c.fetchall()
    conn.close()

    # Форматируем результат
    result = []
    for post in posts:
        result.append({
            'id': post[0],
            'user_id': post[1],
            'title': post[2],
            'content': post[3],
            'tags': post[4],
            'visibility': post[5],
            'username': post[6],
            'created_at': post[7] if post[7] else 'Неизвестно'
        })

    return jsonify(result)
@app.route('/user/<int:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    """
    Возвращает посты конкретного пользователя (только публичные).
    """
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()

    c.execute("""
        SELECT
            p.id,
            p.user_id,
            p.title,
            p.content,
            p.tags,
            p.visibility,
            u.username,
            p.created_at
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.user_id = ? AND p.visibility = 'public'
        ORDER BY p.created_at DESC, p.id DESC
    "", (user_id,))

    posts = c.fetchall()
    conn.close()

    result = []
    for post in posts:
        result.append({
            'id': post[0],
            'user_id': post[1],
            'title': post[2],
            'content': post[3],
            'tags': post[4],
            'visibility': post[5],
            'username': post[6],
            'created_at': post[7] if post[7] else 'Неизвестно'
        })

    return jsonify(result)
@app.route('/posts/search', methods=['GET'])
def search_posts_by_tags():
    """
    Поиск публичных постов по тегам.
    Пример запроса: /posts/search?tags=python,web
    """
    tags_param = request.args.get('tags', '')
    if not tags_param:
        return jsonify({'error': 'Параметр tags обязателен'}), 400

    tags = [tag.strip() for tag in tags_param.split(',') if tag.strip()]
    if not tags:
        return jsonify([]), 200

    conn = sqlite3.connect('blog.db')
    c = conn.cursor()

    # Создаём условия для поиска по нескольким тегам
    conditions = []
    params = []

    for tag in tags:
        conditions.append("p.tags LIKE ?")
        params.append(f'%{tag}%')

    where_clause = " AND ".join(conditions)
    query = f"""
        SELECT
            p.id,
            p.user_id,
            p.title,
            p.content,
            p.tags,
            p.visibility,
            u.username,
            p.created_at
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE {where_clause} AND p.visibility = 'public'
        ORDER BY p.created_at DESC, p.id DESC
    """

    c.execute(query, params)
    posts = c.fetchall()
    conn.close()

    result = []
    for post in posts:
        result.append({
            'id': post[0],
            'user_id': post[1],
            'title': post[2],
            'content': post[3],
            'tags': post[4],
            'visibility': post[5],
            'username': post[6],
            'created_at': post[7] if post[7] else 'Неизвестно'
        })

    return jsonify(result)
def init_db():
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  title TEXT NOT NULL,
                  content TEXT NOT NULL,
                  tags TEXT,
                  visibility TEXT DEFAULT 'public',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    conn.commit()
    conn.close()
@app.route('/post/private', methods=['POST'])
def create_private_post():
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
    tags = data.get('tags', '').strip()

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
            VALUES (?, ?, ?, ?, 'private_request')
        "", (user_id, title, content, tags))
        post_id = c.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Скрытый пост создан успешно',
            'post_id': post_id,
            'title': title,
            'visibility': 'private_request'
        }), 201
    except sqlite3.Error as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка базы данных: {str(e)}'
        }), 500
@app.route('/post/<int:post_id>/request-access', methods=['POST'])
def request_post_access(post_id):
    data = request.json
    if not data or 'requester_id' not in data:
        return jsonify({
            'success': False,
            'error': 'Не заполнен ID запрашивающего пользователя'
        }), 400

    requester_id = data['requester_id']

    try:
        conn = sqlite3.connect('blog.db')
        c = conn.cursor()

        # Проверяем существование поста и его видимость
        c.execute("SELECT user_id, visibility FROM posts WHERE id = ?", (post_id,))
        post = c.fetchone()

        if not post:
            return jsonify({
                'success': False,
                'error': 'Пост не найден'
            }), 404

        if post[1] != 'private_request':
            return jsonify({
                'success': False,
                'error': 'Этот пост не является скрытым по запросу'
            }), 400

        author_id = post[0]

        # Проверяем, не запрашивал ли уже пользователь доступ
        c.execute("""
            SELECT 1 FROM access_requests
            WHERE post_id = ? AND requester_id = ?
        "", (post_id, requester_id))

        if c.fetchone():
            return jsonify({
                'success': False,
                'error': 'Вы уже запрашивали доступ к этому посту'
            }), 409

        # Создаём запрос на доступ
        c.execute("""
            INSERT INTO access_requests (post_id, author_id, requester_id, status)
            VALUES (?, ?, ?, 'pending')
        "", (post_id, author_id, requester_id))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Запрос на доступ отправлен автору поста'
        }), 200
    except sqlite3.Error as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка базы данных: {str(e)}'
        }), 500
@app.route('/access-request/<int:request_id>/approve', methods=['POST'])
def approve_access_request(request_id):
    data = request.json
    if not data or 'approver_id' not in data:
        return jsonify({
            'success': False,
            'error': 'Не заполнен ID утверждающего пользователя'
        }), 400

    approver_id = data['approver_id']

    try:
        conn = sqlite3.connect('blog.db')
        c = conn.cursor()

        # Проверяем запрос и право утверждать
        c.execute("""
            SELECT author_id, post_id FROM access_requests
            WHERE id = ? AND author_id = ? AND status = 'pending'
        "", (request_id, approver_id))

        request_data = c.fetchone()
        if not request_data:
            return jsonify({
                'success': False,
                'error': 'Запрос не найден или у вас нет прав на утверждение'
            }), 403

        post_id = request_data[1]

        # Обновляем статус запроса
        c.execute("UPDATE access_requests SET status = 'approved' WHERE id = ?",
                  (request_id,))

        # Добавляем в таблицу разрешённого доступа
        c.execute("INSERT INTO granted_access (post_id, user_id) VALUES (?, ?)",
                  (post_id, request_data[0]))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Доступ одобрен'
        }), 200
    except sqlite3.Error as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка базы данных: {str(e)}'
        }), 500

