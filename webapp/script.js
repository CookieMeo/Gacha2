// --- ИНИЦИАЛИЗАЦИЯ ДАННЫХ ---
let user = { strawberry: 0, spins: 0, click_power: 1, click_level: 1 };
let pets = [];
let allPets = [];

// Автоматическое определение адреса сервера
const API_URL = window.location.origin;

// --- ФУНКЦИИ ИНТЕРФЕЙСА ---

function showPage(pageId) {
    console.log('Переключение на страницу:', pageId);
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    const activePage = document.getElementById(pageId);
    if (activePage) {
        activePage.classList.add('active');
    }
}

// Обновление UI данных
function updateUI() {
    const strawberryEl = document.getElementById('strawberry-count');
    const spinsEl = document.getElementById('spins-count');
    if (strawberryEl) strawberryEl.innerText = user.strawberry;
    if (spinsEl) spinsEl.innerText = user.spins;
    
    // Обновление данных в профиле
    const profStraw = document.getElementById('profile-strawberry');
    const profSpins = document.getElementById('profile-spins');
    if (profStraw) profStraw.innerText = user.strawberry;
    if (profSpins) profSpins.innerText = user.spins;
}

// --- ЛОГИКА ИГРЫ ---

async function collectStrawberry() {
    try {
        const response = await fetch(`${API_URL}/api/click`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: getUserId() })
        });
        const data = await response.json();
        if (data.success) {
            user.strawberry = data.strawberry;
            updateUI();
        }
    } catch (e) { console.error("Ошибка клика:", e); }
}

async function spinGacha() {
    const resultDiv = document.getElementById('gacha-result');
    if (resultDiv) resultDiv.innerText = "Крутим...";
    
    try {
        const response = await fetch(`${API_URL}/api/spin`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: getUserId() })
        });
        const data = await response.json();
        
        if (data.success) {
            user.spins = data.new_spins_count;
            user.strawberry = data.new_strawberry_count;
            if (resultDiv) resultDiv.innerText = `Выпал: ${data.pet.name} (${data.pet.rarity})`;
            updateUI();
        } else {
            if (resultDiv) resultDiv.innerText = data.error || "Ошибка";
        }
            } catch (e) { console.error("Ошибка гачи:", e); }
}

// Получение ID пользователя из Telegram
function getUserId() {
    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe.user) {
        return window.Telegram.WebApp.initDataUnsafe.user.id;
    }
    return 12345; // Для тестов в браузере
}

// --- БЕЗОПАСНАЯ УСТАНОВКА СОБЫТИЙ ---

function safeAddEventListener(id, event, handler) {
    const el = document.getElementById(id);
    if (el) {
        el.addEventListener(event, handler);
        console.log(`✅ Событие ${event} добавлено для #${id}`);
    } else {
        console.warn(`⚠️ Элемент #${id} не найден. Проверьте index.html`);
    }
}

// Главная инициализация
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM загружен, настраиваю кнопки...");

    // 1. Кнопки навигации
    safeAddEventListener('home-btn', 'click', () => showPage('home'));
    safeAddEventListener('gacha-btn', 'click', () => showPage('gacha'));
    safeAddEventListener('game-btn', 'click', () => showPage('game'));
    safeAddEventListener('profile-btn', 'click', () => showPage('profile'));

    // 2. Игровые кнопки
    safeAddEventListener('spin-1-btn', 'click', spinGacha);
    safeAddEventListener('spin-10-btn', 'click', spinGacha);
    
    // Кнопка промокода (если есть)
    safeAddEventListener('apply-promocode-btn', 'click', async () => {
        const code = document.getElementById('promo-input')?.value;
        if (!code) return;
        // Тут твоя логика промокода...
        console.log("Промокод:", code);
    });

    // Инициализация Telegram WebApp
    if (window.Telegram && window.Telegram.WebApp) {
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.expand();
    }

    // Первое обновление данных
    updateUI();
});




