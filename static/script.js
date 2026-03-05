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
}
