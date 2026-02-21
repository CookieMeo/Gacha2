const tg = window.Telegram.WebApp;
tg.expand();

let user = { strawberry: 0, spins: 0 };

// Функция переключения страниц
function showPage(pageId) {
    // 1. Убираем активный класс у всех страниц
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    // 2. Убираем активный класс у всех кнопок
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    
    // 3. Показываем нужную страницу
    const targetPage = document.getElementById(pageId);
    if (targetPage) targetPage.classList.add('active');
    
    // 4. Подсвечиваем нужную кнопку
    const targetBtn = document.getElementById(pageId + '-btn');
    if (targetBtn) targetBtn.classList.add('active');
}

// Обновление цифр на экране
function updateUI() {
    document.getElementById('strawberry-count').innerText = user.strawberry;
    document.getElementById('strawberry-count-gacha').innerText = user.strawberry;
    document.getElementById('profile-strawberry').innerText = user.strawberry;
    document.getElementById('profile-spins').innerText = user.spins;
}

async function upgradeClicker() {
    const response = await fetch('/api/upgrade', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ user_id: getUserId() })
    });
    const data = await response.json();
    if (data.success) {
        alert("Уровень повышен!");
        location.reload(); // Проще всего обновить данные так
    } else {
        alert("Недостаточно клубники!");
    }
}

// Клик по клубнике
function collectStrawberry() {
    user.strawberry += 1; // Пока без бэкенда просто прибавляем
    updateUI();
    // Эффект вибрации для Telegram
    if (tg.HapticFeedback) tg.HapticFeedback.impactOccurred('medium');
}

async function buySpins(amount) {
    const response = await fetch('/api/buy_spins', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ user_id: getUserId(), amount: amount })
    });
    const data = await response.json();
    if (data.success) {
        alert("Крутки куплены!");
        updateUI();
    }
}

function updatePityCounters(user) {
    document.getElementById('pity-red').innerText = user.pity_red;
    document.getElementById('pity-orange').innerText = user.pity_orange;
    document.getElementById('pity-yellow').innerText = user.pity_yellow;
    document.getElementById('pity-green').innerText = user.pity_green;
    document.getElementById('pity-lightblue').innerText = user.pity_lightblue;
    document.getElementById('pity-blue').innerText = user.pity_blue;
    document.getElementById('pity-purple').innerText = user.pity_puple;

// Настройка кнопок при загрузке
document.addEventListener('DOMContentLoaded', () => {
    // Слушатели для навигации
    document.getElementById('home-btn').onclick = () => showPage('home');
    document.getElementById('gacha-btn').onclick = () => showPage('gacha');
    document.getElementById('game-btn').onclick = () => showPage('game');
    document.getElementById('profile-btn').onclick = () => showPage('profile');

    // Слушатель для кликера
    document.getElementById('collect-btn').onclick = collectStrawberry;

    // Слушатель для гачи
    document.getElementById('spin-btn').onclick = () => {
        if (user.strawberry >= 100) {
            user.strawberry -= 100;
            user.spins += 1;
            document.getElementById('gacha-result').innerText = "Выпал обычный Кот! 🐱";
            updateUI();
        } else {
            alert("Недостаточно клубники!");
        }
    };
    
    updateUI();
});

