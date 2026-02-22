// 1. Константы в самом верху (чтобы не было ReferenceError)
const tg = window.Telegram.WebApp;
const uid = tg.initDataUnsafe.user?.id || 12345;

const UPGRADE_COSTS = {
    2: 10, 3: 40, 4: 90, 5: 160, 6: 250, 7: 360, 8: 490, 9: 640, 10: 810, 11: 4000
};

const GIFS = {
    "Красное": "assets/red.gif",
    "Оранжевое": "assets/orange.gif",
    "Желтое": "assets/yellow.gif", 
    "Зеленое": "assets/green.gif",
    "Голубое": "assets/lightblue.gif",
    "Синее": "assets/blue.gif", 
    "Фиолетовое": "assets/purple.gif",
    "default": "assets/purple.gif"
};

// 2. Универсальная функция запросов
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

// 3. Обновление экрана (Цены и данные)
async function updateUI() {
    const u = await api('/get_user', { user_id: uid });
    if (!u) return;

    // Текст
    const setT = (id, val) => { if(document.getElementById(id)) document.getElementById(id).innerText = val; };
    
    setT('straw-count', u.strawberry);
    setT('gacha-straw', u.strawberry);
    setT('spin-count', u.spins);
    setT('lvl-display', "Уровень " + u.click_level);
    setT('p-red', u.pity_red);
    setT('p-blu', u.pity_blue);

    // КНОПКА УЛУЧШЕНИЯ (Актуальная цена)
    const upBtn = document.getElementById('upgrade-btn');
    if (upBtn) {
        const nextPrice = UPGRADE_COSTS[u.click_level + 1];
        if (nextPrice) {
            upBtn.innerText = `Улучшить (${nextPrice} 🍓)`;
        } else {
            upBtn.innerText = "Макс. уровень";
        }
    }

    if (document.getElementById('home').classList.contains('active')) updateInventory();
}

// 4. Гача
async function spin(count) {
    const res = await api('/spin', { user_id: uid, count: count });
    if (!res.success) return alert(res.error);

    const mainPet = res.pets[0];
    const overlay = document.getElementById('gacha-overlay');
    overlay.classList.remove('hidden');
    document.getElementById('res-card').classList.add('hidden');
    document.getElementById('anim-box').classList.remove('hidden');
    
    // Берем гифку из объекта GIFS
    document.getElementById('gacha-gif').src = GIFS[mainPet.rarity] || GIFS.default;

    setTimeout(() => {
        document.getElementById('anim-box').classList.add('hidden');
        document.getElementById('res-card').classList.remove('hidden');
        document.getElementById('res-img').src = mainPet.image_url || 'assets/strawberry.png';
        document.getElementById('res-name').innerText = mainPet.name;
        updateUI();
    }, 3000);
}

// 5. Инвентарь
async function updateInventory() {
    const items = await api('/get_inventory', { user_id: uid });
    const grid = document.getElementById('inventory-grid');
    if (!grid) return;
    
    grid.innerHTML = "";
    if (!items || items.length === 0) {
        grid.innerHTML = `<p style="grid-column: 1/3; text-align: center; color: gray;">Тут пока пусто</p>`;
        return;
    }
    
    items.forEach(item => {
        grid.innerHTML += `
            <div class="pet-item ${item.pet_rarity}">
                <img src="${item.pet_image || 'assets/strawberry.png'}">
                <p><b>${item.pet_name}</b></p>
                <small>${item.pet_rarity}</small>
                <!-- <p class="skill-text">${item.pet_skill}</p> -->
            </div>
        `;
    });
}

// Прочее
function showPage(id) {
    // 1. Переключаем страницы
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(id).classList.add('active');

    // 2. Переключаем подсветку кнопок в футере
    document.querySelectorAll('nav button').forEach(btn => btn.classList.remove('active-nav'));
    const activeBtn = document.getElementById(id + '-btn');
    if (activeBtn) activeBtn.classList.add('active-nav');

    updateUI();
}

function closeGacha() { document.getElementById('gacha-overlay').classList.add('hidden'); }

async function buy(count) {
    const res = await api('/buy', { user_id: uid, count: count });
    if (res.success) updateUI(); else alert("Мало клубники!");
}

document.addEventListener('DOMContentLoaded', () => {
    tg.expand();
    document.getElementById('home-btn').onclick = () => showPage('home');
    document.getElementById('gacha-btn').onclick = () => showPage('gacha');
    document.getElementById('game-btn').onclick = () => showPage('game');
    document.getElementById('profile-btn').onclick = () => showPage('profile');

    document.getElementById('collect-btn').onclick = async () => {
        await api('/click', { user_id: uid });
        updateUI();
    };
    document.getElementById('upgrade-btn').onclick = async () => {
        const res = await api('/upgrade', { user_id: uid });
        if (res.success) updateUI(); else alert("Мало клубники!");
    };
    document.getElementById('spin-1').onclick = () => spin(1);
    document.getElementById('spin-10').onclick = () => spin(10);
    updateUI();
});

