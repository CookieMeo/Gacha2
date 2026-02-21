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

// Клик по клубнике
function collectStrawberry() {
    user.strawberry += 1; // Пока без бэкенда просто прибавляем
    updateUI();
    // Эффект вибрации для Telegram
    if (tg.HapticFeedback) tg.HapticFeedback.impactOccurred('medium');
}

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
