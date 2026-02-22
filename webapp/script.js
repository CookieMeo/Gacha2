
const tg = window.Telegram.WebApp;
const uid = tg.initDataUnsafe.user?.id || 12345;

// --- КОНСТАНТЫ ---
const UPGRADE_COSTS = {
    2: 10, 3: 40, 4: 90, 5: 160, 6: 250, 7: 360, 8: 490, 9: 640, 10: 810, 11: 4000
};

// !!! ЗАМЕНИ НА ПРАВИЛЬНЫЕ ПУТИ К ТВОИМ ГИФКАМ !!!
// !!! Скорее всего, они лежат в папке assets !!!
const GIFS = {
    "Красное": "assets/red.gif", 
    "Оранжевое": "assets/orange.gif",
    "Жёлтое": "assets/yellow.gif",
    "Зеленое": "assets/green.gif",
    "Голубое": "assets/lightblue.gif",
    "Синее": "assets/blue.gif",
    "Фиолетовое": "assets/purple.gif", // Для обычных
    "default": "assets/purple.gif"     // На случай ошибки
};

// --- API ЗАПРОСЫ ---
async function api(path, body) {
    try {
        const r = await fetch('/api' + path, {
            method: 'POST', 
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        });
        return await r.json();
    } catch (e) { 
        console.error(`Ошибка API (${path}):`, e);
        return { success: false }; 
    }
}

// --- ОБНОВЛЕНИЕ ИНТЕРФЕЙСА ---
async function updateUI() {
    const u = await api('/get_user', { user_id: uid });
    if (!u) {
        console.error("Не удалось получить данные пользователя!");
        return;
    }

    const safeSet = (id, val) => { 
        const el = document.getElementById(id);
        if (el) el.innerText = val; 
    };
    
    safeSet('straw-count', u.strawberry);
    safeSet('gacha-straw', u.strawberry);
    safeSet('spin-count', u.spins);
    safeSet('lvl-display', "Уровень " + u.click_level);
    safeSet('p-red', u.pity_red);
    safeSet('p-ora', u.pity_orange);
    safeSet('p-yel', u.pity_yellow);
    safeSet('p-gre', u.pity_green);
    safeSet('p-lbu', u.pity_lightblue);
    safeSet('p-blu', u.pity_blue);

    // Обновляем кнопку улучшения
    const upBtn = document.getElementById('upgrade-btn');
    if (upBtn) {
        const cost = UPGRADE_COSTS[u.click_level + 1];
        if (cost !== undefined) {
            upBtn.innerText = `Улучшить (${cost} 🍓)`;
            upBtn.disabled = false;
        } else {
            upBtn.innerText = "Макс. уровень";
            upBtn.disabled = true;
        }
    }

    // Обновляем инвентарь, если мы на странице "Дом"
    if (document.getElementById('home').classList.contains('active')) {
        updateInventory();
    }
}

async function updateInventory() {
    const items = await api('/get_inventory', { user_id: uid });
    const grid = document.getElementById('inventory-grid');
    if (!grid || !items) return;
    
    grid.innerHTML = "";
    if (items.length === 0) {
        grid.innerHTML = `<p style="grid-column: 1/3; text-align: center;">У вас пока нет питомцев</p>`;
        return;
    }
    
    items.forEach(item => {
        grid.innerHTML += `
            <div class="pet-item">
                <img src="${item.pet_image || 'assets/strawberry.png'}">
                <p><b>${item.pet_name}</b></p>
                <small>${item.pet_rarity}</small>
            </div>
        `;
    });
}

// --- ФУНКЦИИ ДЛЯ КНОПОК ---

function showPage(id) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    updateUI(); // Обновляем данные при переходе
}

async function spin(count) {
    console.log(`Кручу гачу x${count}`);
    const res = await api('/spin', { user_id: uid, count: count });
    
    if (!res.success) {
        console.error("Ошибка гачи:", res.error);
        return alert(res.error || "Ошибка при крутке");
    }

    const mainPet = res.pets[0]; // Берем первого питомца для анимации
    const overlay = document.getElementById('gacha-overlay');
    const animBox = document.getElementById('anim-box');
    const resCard = document.getElementById('res-card');
    
    overlay.classList.remove('hidden');
    resCard.classList.add('hidden');
    animBox.classList.remove('hidden');
    
    const gifSrc = GIFS[mainPet.rarity] || GIFS.default;
    console.log(`Анимация для ${mainPet.rarity}: ${gifSrc}`);
    document.getElementById('gacha-gif').src = gifSrc;

    // Показываем карточку результата через 3 секунды
    setTimeout(() => {
        animBox.classList.add('hidden');
        resCard.classList.remove('hidden');
        
        document.getElementById('res-img').src = mainPet.image_url || 'assets/strawberry.png';
        document.getElementById('res-name').innerText = mainPet.name;
        document.getElementById('res-rarity').innerText = mainPet.rarity;
        
        updateUI(); // Обновляем счетчики (крутки, гаранты)
    }, 3000); 
}

function closeGacha() {
    document.getElementById('gacha-overlay').classList.add('hidden');
}

async function buy(count) {
    const res = await api('/buy', { user_id: uid, count: count });
    if (res.success) updateUI(); else alert("Недостаточно клубники!");
}

// --- ИНИЦИАЛИЗАЦИЯ ---
document.addEventListener('DOMContentLoaded', () => {
    tg.expand();
    
    // Навигация
    document.getElementById('home-btn').onclick = () => showPage('home');
    document.getElementById('gacha-btn').onclick = () => showPage('gacha');
    document.getElementById('game-btn').onclick = () => showPage('game');
    document.getElementById('profile-btn').onclick = () => showPage('profile');

    // Кнопки игры
    const collectBtn = document.getElementById('collect-btn');
    if(collectBtn) collectBtn.onclick = async () => {
        await api('/click', { user_id: uid });
        updateUI();
    };

    const upgradeBtn = document.getElementById('upgrade-btn');
    if(upgradeBtn) upgradeBtn.onclick = async () => {
        const res = await api('/upgrade', { user_id: uid });
        if (res.success) updateUI(); else alert("Мало клубники!");
    };

    // Кнопки гачи
    if(document.getElementById('spin-1')) document.getElementById('spin-1').onclick = () => spin(1);
    if(document.getElementById('spin-10')) document.getElementById('spin-10').onclick = () => spin(10);

    updateUI();
});
