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
@app.route('/posts/sorted-by-tags', methods=['GET'])
def get_posts_sorted_by_tags():
    """
    Возвращает посты, отсортированные по тегам.
    Параметры:
    - tags: строка с тегами через запятую
    - sort_order: 'asc' или 'desc' (по умолчанию 'asc')
    Пример: /posts/sorted-by-tags?tags=python,web&sort_order=asc
    """
    tags_param = request.args.get('tags', '')
    sort_order = request.args.get('sort_order', 'asc').lower()

    if not tags_param:
        return jsonify({'error': 'Параметр tags обязателен'}), 400

    tags = [tag.strip() for tag in tags_param.split(',') if tag.strip()]
    if not tags:
        return jsonify([]), 200

    # Проверка корректности параметра сортировки
    if sort_order not in ['asc', 'desc']:
        return jsonify({'error': 'sort_order должен быть asc или desc'}), 400

    conn = sqlite3.connect('blog.db')
    c = conn.cursor()

    # Создаём условия для поиска по нескольким тегам
    conditions = []
    params = []

    for tag in tags:
        conditions.append("p.tags LIKE ?")
        params.append(f'%{tag}%')

    where_clause = " AND ".join(conditions)
    order_clause = 'p.created_at ASC' if sort_order == 'asc' else 'p.created_at DESC'

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
        ORDER BY {order_clause}, p.id DESC
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
@app.route('/tags', methods=['GET'])
def get_all_tags():
    """Возвращает список всех уникальных тегов в системе"""
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT tags FROM posts WHERE tags IS NOT NULL AND tags != ''")
    tag_rows = c.fetchall()
    conn.close()

    # Разбиваем составные теги и собираем уникальные
    all_tags = set()
    for row in tag_rows:
        if row[0]:
            tags_list = [tag.strip().lower() for tag in row[0].split(',')]
            all_tags.update(tags_list)

    sorted_tags = sorted(list(all_tags))
    return jsonify(sorted_tags)
