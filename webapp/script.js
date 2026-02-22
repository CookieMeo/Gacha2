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

    // Обновляем текст
    const safeSet = (id, val) => { if(document.getElementById(id)) document.getElementById(id).innerText = val; };
    
    safeSet('straw-count', u.strawberry);
    safeSet('gacha-straw', u.strawberry);
    safeSet('spin-count', u.spins);
    safeSet('lvl-display', "Уровень " + u.click_level);
    safeSet('p-red', u.pity_red);
    safeSet('p-blu', u.pity_blue);

    // Инвентарь обновляем только если мы на странице Дома
    if (document.getElementById('home').classList.contains('active')) {
        updateInventory();
    }
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
    updateUI(); // Обновляем данные при переходе
}

// Сама гача
async function spin(count) {
    const res = await api('/spin', { user_id: uid, count: count });
    if (!res.success) return alert(res.error);

    const mainPet = res.pets[0];
    const overlay = document.getElementById('gacha-overlay');
    overlay.classList.remove('hidden');
    document.getElementById('res-card').classList.add('hidden');
    document.getElementById('anim-box').classList.remove('hidden');
    
    // Анимация 3 сек
    setTimeout(() => {
        document.getElementById('anim-box').classList.add('hidden');
        document.getElementById('res-card').classList.remove('hidden');
        document.getElementById('res-img').src = mainPet.image_url || 'assets/strawberry.png';
        document.getElementById('res-name').innerText = mainPet.name;
        updateUI();
    }, 3000);
}

async function spin(count) {
    const res = await api('/spin', { user_id: uid, count: count });
    if (!res.success) return alert(res.error);

    const mainPet = res.pets[0];
    const overlay = document.getElementById('gacha-overlay');
    const gif = document.getElementById('gacha-gif');
    
    overlay.classList.remove('hidden');
    document.getElementById('res-card').classList.add('hidden');
    document.getElementById('anim-box').classList.remove('hidden');
    
    gif.src = GIFS[mainPet.rarity] || GIFS.default;

    setTimeout(() => {
        document.getElementById('anim-box').classList.add('hidden');
        const card = document.getElementById('res-card');
        card.classList.remove('hidden');
        document.getElementById('res-img').src = mainPet.image_url;
        document.getElementById('res-name').innerText = mainPet.name;
        document.getElementById('res-rarity').innerText = mainPet.rarity;
        updateUI();
    }, 3000); // 3 секунды анимации
}

function closeGacha() {
    document.getElementById('gacha-overlay').classList.add('hidden');
}

// Обновление инвентаря на странице "ДОМ"
async function updateInventory() {
    const items = await api('/get_inventory', { user_id: uid });
    const grid = document.getElementById('inventory-grid');
    if (!grid || !items) return;
    
    grid.innerHTML = "";
    if (items.length === 0) {
        grid.innerHTML = "<p style='grid-column: 1/3'>У вас пока нет питомцев</p>";
        return;
    }
    
    items.forEach(item => {
        grid.innerHTML += 
            <div class="pet-item">
                <img src="${item.pet_image || 'assets/strawberry.png'}">
                <p><b>${item.pet_name}</b></p>
                <small>${item.pet_rarity}</small>
            </div>
        ;
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
}

