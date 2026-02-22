const tg = window.Telegram.WebApp;
const uid = tg.initDataUnsafe.user?.id || 12345;

const UPGRADE_COSTS = {
    2: 10, 3: 40, 4: 90, 5: 160, 6: 250, 7: 360, 8: 490, 9: 640, 10: 810, 11: 4000
};

const RARITY_GIFS = {
    "Красное": "assets/red.gif",
    "Оранжевое": "assets/orange.gif",
    "Желтое": "assets/yellow.gif",
    "Зеленое": "assets/green.gif",
    "Голубое": "assets/lightblue.gif",
    "Синее": "assets/blue.gif",
    "default": "assets/purple.gif" // обычная гифка
};

async function api(path, body) {
    try {
        const r = await fetch('/api' + path, {
            method: 'POST', 
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        });
        return await r.json();
    } catch (e) { return { success: false }; }
}

async function updateUI() {
    const u = await api('/get_user', { user_id: uid });
    if (!u) return;

    // Обновляем клубнику ВЕЗДЕ, где есть эти ID
    if (document.getElementById('straw-count')) document.getElementById('straw-count').innerText = u.strawberry;
    if (document.getElementById('gacha-straw')) document.getElementById('gacha-straw').innerText = u.strawberry;

    // ОБНОВЛЯЕМ КРУТКИ
    if (document.getElementById('spin-count')) document.getElementById('spin-count').innerText = u.spins;

    // Обновляем уровень и кнопку
    if (document.getElementById('lvl-display')) document.getElementById('lvl-display').innerText = "Уровень " + u.click_level;
    
    const upBtn = document.getElementById('upgrade-btn');
    if (upBtn) {
        const cost = UPGRADE_COSTS[u.click_level + 1];
        if (cost) upBtn.innerText = `Улучшить (${cost} 🍓)`;
        else upBtn.innerText = "Макс. уровень";
    }

    // Обновляем гаранты в Гаче
    if (document.getElementById('p-red')) document.getElementById('p-red').innerText = u.pity_red;
    if (document.getElementById('p-blu')) document.getElementById('p-blu').innerText = u.pity_blue;
}

async function collectStrawberry() {
    const res = await api('/click', { user_id: uid });
    if (res.success) {
        updateUI();
    }
}

async function upgradeClicker() {
    const res = await api('/upgrade', { user_id: uid });
    if (res.success) {
        updateUI();
    } else {
        alert("Недостаточно клубники!");
    }
}

// Покупка круток
async function buy(count) {
    const res = await api('/buy', { user_id: uid, count: count });
    if (res.success) {
        updateUI(); // Сразу обновит и клубнику, и крутки на экране
    } else {
        alert("Недостаточно клубники!");
    }
}

function showPage(id) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

// Сама гача
async function spin(count) {
    console.log("Пытаюсь крутить гачу: x" + count);
    const res = await api('/spin', { user_id: uid, count: count });
    
    if (res.success) {
        console.log("Успех! Выпали: ", res.pets);
        const names = res.pets.map(p => `${p.name} (${p.rarity})`).join(', ');
        document.getElementById('gacha-res').innerText = "Выпало: " + names;
        updateUI(); // Обновит счетчик круток на экране
    } else {
        console.error("Ошибка гачи:", res.error);
        alert(res.error || "Ошибка при крутке");
    }
}

async function spin(count) {
    const res = await api('/spin', { user_id: uid, count: count });
    if (!res.success) return alert(res.error);

    // Берем самого редкого питомца из выпавших для выбора анимации
    const mainPet = res.pets[0]; 
    const gifUrl = RARITY_GIFS[mainPet.rarity] || RARITY_GIFS["default"];

    // 1. Показываем оверлей и гифку
    const overlay = document.getElementById('gacha-overlay');
    const gifImg = document.getElementById('gacha-gif');
    const resultCard = document.getElementById('result-card');
    const animContainer = document.getElementById('animation-container');

    overlay.classList.remove('hidden');
    resultCard.classList.add('hidden');
    animContainer.classList.remove('hidden');
    gifImg.src = gifUrl;

    // 2. Через 3 секунды (длина гифки) показываем результат
    setTimeout(() => {
        animContainer.classList.add('hidden');
        resultCard.classList.remove('hidden');
        
        document.getElementById('res-rarity-text').innerText = mainPet.rarity;
        document.getElementById('res-pet-img').src = mainPet.image_url || 'assets/default_pet.png';
        document.getElementById('res-pet-name').innerText = mainPet.name;
        
        // Если крутили x10, можно добавить "и еще 9 питомцев..."
        updateUI();
        updateInventory(); // Обновляем инвентарь в фоне
    }, 3000); 
}

function closeGacha() {
    document.getElementById('gacha-overlay').classList.add('hidden');
}

// Обновление инвентаря на странице "ДОМ"
async function updateInventory() {
    const pets = await api('/get_inventory', { user_id: uid });
    const grid = document.getElementById('inventory-grid');
    if (!grid) return;
    
    grid.innerHTML = "";
    pets.forEach(pet => {
        const card = document.createElement('div');
        card.className = `pet-card ${pet.pet_rarity}`;
        card.innerHTML = `
            <img src="${pet.pet_image || 'assets/default_pet.png'}">
            <h4>${pet.pet_name}</h4>
            <small>${pet.pet_rarity}</small>
        `;
        grid.appendChild(card);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    tg.expand();
    
    // Привязка клика и улучшения
    if (document.getElementById('collect-btn')) document.getElementById('collect-btn').onclick = async () => {
        await api('/click', { user_id: uid });
        updateUI();
    };
    
    if (document.getElementById('upgrade-btn')) document.getElementById('upgrade-btn').onclick = async () => {
        const res = await api('/upgrade', { user_id: uid });
        if (res.success) updateUI(); else alert("Мало клубники!");
    };
    
    // Навигация
    document.getElementById('home-btn').onclick = () => showPage('home');
    document.getElementById('gacha-btn').onclick = () => showPage('gacha');
    document.getElementById('game-btn').onclick = () => showPage('game');
    document.getElementById('profile-btn').onclick = () => showPage('profile');

    // Кнопки
    if (document.getElementById('collect-btn')) document.getElementById('collect-btn').onclick = collectStrawberry;
    if (document.getElementById('upgrade-btn')) document.getElementById('upgrade-btn').onclick = upgradeClicker;
    if (document.getElementById('spin-1')) document.getElementById('spin-1').onclick = () => spin(1);
    if (document.getElementById('spin-10')) document.getElementById('spin-10').onclick = () => spin(10);

    updateUI();
});










