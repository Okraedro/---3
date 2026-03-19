// Функция регистрации
function register() {
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        const messageDiv = document.getElementById('reg-message');
        if (data.success) {
            messageDiv.innerHTML = `<div class="message success">${data.message}</div>`;
            // Очистка полей
            document.getElementById('reg-username').value = '';
            document.getElementById('reg-password').value = '';
        } else {
            messageDiv.innerHTML = `<div class="message error">Ошибка: ${data.error}</div>`;
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        document.getElementById('reg-message').innerHTML =
            '<div class="message error">Произошла сетевая ошибка</div>';
    });
}

// Функция входа
function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        const messageDiv = document.getElementById('login-message');
        if (data.success) {
            messageDiv.innerHTML =
                `<div class="message success">${data.message}. ID: ${data.user_id}</div>`;
            // Здесь можно сохранить user_id в localStorage или перейти на главную страницу
            localStorage.setItem('currentUser', JSON.stringify(data));
            // Очистка полей
            document.getElementById('login-username').value = '';
            document.getElementById('login-password').value = '';
        } else {
            messageDiv.innerHTML = `<div class="message error">Ошибка: ${data.error}</div>`;
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        document.getElementById('login-message').innerHTML =
            '<div class="message error">Произошла сетевая ошибка</div>';
    });

    function createPost() {
    // Получаем данные из формы
    const title = document.getElementById('post-title').value;
    const content = document.getElementById('post-content').value;
    const tags = document.getElementById('post-tags').value;
    const visibility = document.getElementById('post-visibility').value;

    // Берём ID пользователя из localStorage (сохраняется при входе)
    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    if (!currentUser) {
        alert('Сначала войдите в систему!');
        return;
    }

    const user_id = currentUser.user_id;

    fetch('/post', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: user_id,
            title: title,
            content: content,
            tags: tags,
            visibility: visibility
        })
    })
    .then(response => response.json())
    .then(data => {
        const messageDiv = document.getElementById('post-message');
        if (data.success) {
            messageDiv.innerHTML =
                `<div class="message success">${data.message}. ID поста: ${data.post_id}</div>`;
            // Очистка формы после успешной отправки
            document.getElementById('post-title').value = '';
            document.getElementById('post-content').value = '';
            document.getElementById('post-tags').value = '';
        } else {
            messageDiv.innerHTML = `<div class="message error">Ошибка: ${data.error}</div>`;
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        document.getElementById('post-message').innerHTML =
            '<div class="message error">Произошла сетевая ошибка</div>';
    });
}
    function followUser() {
    const follower_id = parseInt(document.getElementById('follower-id').value);
    const following_id = parseInt(document.getElementById('following-id').value);

    fetch('/follow', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ follower_id, following_id })
    })
    .then(response => response.json())
    .then(data => {
        const messageDiv = document.getElementById('follow-message');
        if (data.success) {
            messageDiv.innerHTML =
                `<div class="message success">${data.message}</div>`;
        } else {
            messageDiv.innerHTML = `<div class="message error">Ошибка: ${data.error}</div>`;
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        document.getElementById('follow-message').innerHTML =
            '<div class="message error">Произошла сетевая ошибка</div>';
    });
}

function unfollowUser() {
    const follower_id = parseInt(document.getElementById('follower-id').value);
    const following_id = parseInt(document.getElementById('following-id').value);

    fetch('/unfollow', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ follower_id, following_id })
    })
    .then(response => response.json())
    .then(data => {
        const messageDiv = document.getElementById('follow-message');
        if (data.success) {
            messageDiv.innerHTML =
                `<div class="message success">${data.message}</div>`;
        } else {
            messageDiv.innerHTML = `<div class="message error">Ошибка: ${data.error}</div>`;
        }
    })
}
    function loadUserFeed() {
    const user_id = parseInt(document.getElementById('feed-user-id').value);

    fetch(`/feed/${user_id}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(posts => {
        const container = document.getElementById('feed-container');
        const messageDiv = document.getElementById('feed-message');

        if (posts.length === 0) {
            container.innerHTML = '<p>Пока нет постов от пользователей, на которых вы подписаны</p>';
            return;
        }

        // Формируем HTML для отображения постов
        let feedHTML = '<div class="feed-posts">';
        posts.forEach(post => {
            feedHTML += `
                <div class="post-card">
                    <h3>${post.title}</h3>
            <p><strong>Автор:</strong> ${post.username} (ID: ${post.user_id})</p>
            <p>${post.content}</p>
            ${post.tags ? `<p><strong>Теги:</strong> ${post.tags}</p>` : ''}
            <small>Опубликовано: ${post.created_at}</small>
            <hr>
        </div>
            `;
        });
        feedHTML += '</div>';
        container.innerHTML = feedHTML;
        messageDiv.innerHTML = `<div class="message success">Лента обновлена успешно</div>`;
    })
    .catch(error => {
        console.error('Ошибка загрузки ленты:', error);
        document.getElementById('feed-message').innerHTML =
            '<div class="message error">Произошла ошибка при загрузке ленты</div>';
    });
}

function loadAllUsers() {
    fetch('/users', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(users => {
        const usersList = document.getElementById('users-list');

        if (users.length === 0) {
            usersList.innerHTML = '<p>Пользователей не найдено</p>';
            return;
        }

        // Формируем список пользователей с кнопками подписки
        let usersHTML = '<div class="users-grid">';
        users.forEach(user => {
            usersHTML += `
                <div class="user-card">
            <p><strong>${user.username}</strong> (ID: ${user.id})</p>
            <button onclick="subscribeToUser(${user.id})">Подписаться</button>
        </div>
            `;
        });
        usersHTML += '</div>';
        usersList.innerHTML = usersHTML;
    })
    .catch(error => {
        console.error('Ошибка загрузки пользователей:', error);
        document.getElementById('users-list').innerHTML =
            '<div class="message error">Произошла ошибка при загрузке списка пользователей</div>';
    });
}

function subscribeToUser(following_id) {
    // Берём ID текущего пользователя из localStorage
    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    if (!currentUser) {
        alert('Сначала войдите в систему!');
        return;
    }

    const follower_id = currentUser.user_id;

    // Используем существующую функцию подписки
    fetch('/follow', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ follower_id, following_id })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            // Обновляем список пользователей
            loadAllUsers();
        } else {
            alert('Ошибка: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Ошибка подписки:', error);
        alert('Произошла сетевая ошибка');
    });
}

