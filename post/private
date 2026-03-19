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
    tags = data.get('tags', '').strip()  # теги могут быть необязательными
    visibility = data.get('visibility', 'public')

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
        post_id = c.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Пост создан успешно',
            'post_id': post_id,
            'tags': tags
        }), 201
    except sqlite3.Error as e:
        return jsonify({
            'success': False,
            'error': f'Ошибка базы данных: {str(e)}'
        }), 500
