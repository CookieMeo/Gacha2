// 1. Инициализация переменных в самом начале
const tg = window.Telegram.WebApp;
const USER_ID = tg.initDataUnsafe?.user?.id || 12345;
let currentBanner = 1; 

const UPGRADE_COSTS = {
    1: [0, 1], 2: [10, 2], 3: [40, 3], 4: [90, 4], 5: [160, 5], 
    6: [250, 6], 7: [360, 7], 8: [490, 8], 9: [640, 9], 10: [810, 10], 11: [4000, 100]
};

const GIFS = {
    "Красное": "assets/red.gif",
    "Оранжевое": "assets/orange.gif",
    "Жёлтое": "assets/yellow.gif",
    "Зеленое": "assets/green.gif",
    "Голубое": "assets/lightblue.gif",
    "Синее": "assets/blue.gif",
    "Фиолетовое": "assets/purple.gif",
    "default": "assets/purple.gif"
};

// Глобальный объект данных (синхронизируется с БД)
let userData = {
    clicks: 0,
    level: 1,
    upgrade_cost: 10
};

// --- ЛОГИКА ПЕРЕКЛЮЧЕНИЯ ВКЛАДОК (Твоя существующая) ---
function showTab(tabId) {
    // Скрываем все секции
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    // Показываем нужную
    const activeTab = document.getElementById(tabId);
    if (activeTab) {
        activeTab.style.display = 'block';
    }

    // Если открыли профиль — обновляем данные там еще раз на всякий случай
    if (tabId === 'profile') {
        updateProfileUI();
    }
}
const gachaAnimation = document.getElementById('gacha-animation'); 

function playAnimation() {
    // ВАЖНО: Проверь, что файл называется именно так: spin.gif (маленькими буквами)
    gachaAnimation.src = 'assets/spin.gif'; 
    gachaAnimation.style.display = 'block';

    setTimeout(() => {
        gachaAnimation.style.display = 'none';
        // Дальше идет твоя логика показа выпавшего животного
    }, 3000); // 3 секунды на анимацию
}

// --- РАБОТА С СЕРВЕРОМ (НОВАЯ ЛОГИКА) ---

// 1. Загрузка данных при старте
async function fetchUserData() {
    console.log("Запрос данных для пользователя:", USER_ID);
    const loadingScreen = document.getElementById('loading-screen');

    try {
        // Запрос к твоему API в bot.py
        const response = await fetch(`/api/user/${USER_ID}`);
        if (!response.ok) throw new Error('Пользователь не найден или ошибка сервера');
        
        const data = await response.json();
        
        // Обновляем локальные данные данными из БД
        userData.clicks = data.clicks;
        userData.level = data.level;
        userData.upgrade_cost = data.upgrade_cost || (data.level * 10); // если нет в БД, считаем сами

        console.log("Данные успешно загружены из БД:", userData);
    } catch (error) {
        console.error("Ошибка при загрузке данных:", error);
        // Если ошибка (например, сервер еще не проснулся), оставляем дефолтные 0
    } finally {
        // В ЛЮБОМ СЛУЧАЕ убираем экран загрузки через секунду
        if (loadingScreen) {
            setTimeout(() => {
                loadingScreen.style.display = 'none';
                updateUI();
            }, 500);
        }
    }
}

// 2. Сохранение данных на сервер (автосохранение)
async function saveToServer() {
    try {
        await fetch('/api/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: USER_ID,
                clicks: userData.clicks,
                level: userData.level
            })
        });
    } catch (e) {
        console.warn("Не удалось сохранить данные на сервер (возможно, оффлайн)");
    }
}

// --- ЛОГИКА ИГРЫ (Клик и Улучшение) ---

function updateUI() {
    const scoreEl = document.getElementById('score');
    const levelEl = document.getElementById('level');
    const upgradeBtn = document.getElementById('upgrade-btn');

    if (scoreEl) scoreEl.innerText = `Клубника: ${userData.clicks}`;
    if (levelEl) levelEl.innerText = `Уровень ${userData.level}`;
    if (upgradeBtn) upgradeBtn.innerText = `Улучшить (${userData.upgrade_cost})`;
    
    updateProfileUI();
}

function updateProfileUI() {
    const profId = document.getElementById('prof-id');
    const profClicks = document.getElementById('prof-clicks');
    
    if (profId) profId.innerText = `ID: ${USER_ID}`;
    if (profClicks) profClicks.innerText = `Всего собрано: ${userData.clicks}`;
}

// Клик по клубнике
const strawberryImg = document.getElementById('strawberry');
if (strawberryImg) {
    strawberryImg.addEventListener('click', () => {
        userData.clicks += 1; // Можно умножать на уровень: + (1 * userData.level)
        updateUI();
        saveToServer(); // Отправляем в БД
    });
}

// Кнопка улучшения
const upgradeBtn = document.getElementById('upgrade-btn');
if (upgradeBtn) {
    upgradeBtn.addEventListener('click', () => {
        if (userData.clicks >= userData.upgrade_cost) {
            userData.clicks -= userData.upgrade_cost;
            userData.level += 1;
            userData.upgrade_cost = userData.level * 10;
            updateUI();
            saveToServer();
            alert("Уровень повышен!");
        } else {
            alert("Недостаточно клубники!");
        }
    });
}

// --- ИНИЦИАЛИЗАЦИЯ ---

window.onload = () => {
    // 1. Сразу показываем главную вкладку
    showTab('home');
    
    // 2. Идем в базу за данными этого юзера
    fetchUserData();
};

