
// 1. Инициализация переменных в самом начале
const tg = window.Telegram.WebApp;
const user = tg.initDataUnsafe?.user;
const uid = user?.id || 12345;
let currentBanner = 1; 

const UPGRADE_COSTS = {
    1: [0, 1], 2: [10, 2], 3: [40, 3], 4: [90, 4], 5: [160, 5], 
    6: [250, 6], 7: [360, 7], 8: [490, 8], 9: [640, 9], 10: [810, 10], 11: [4000, 100]
};

const GIFS = {
    "Красное": "assets/red_gacha.gif",
    "Оранжевое": "assets/orange_gacha.gif",
    "Жёлтое": "assets/yellow_gacha.gif",
    "Зелене": "assets/green_gacha.gif",
    "Голубое": "assets/lightblue_gacha.gif",
    "Синее": "assets/blue_gacha.gif",
    "Фиолетовое": "assets/purple_gacha.gif",
    "default": "assets/default_gacha.gif"
};

// 2. Функция API
async function api(path, data) {
    try {
        const res = await fetch('/api' + path, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await res.json();
    } catch (e) {
        console.error("API Error:", e);
        return { success: false, error: "Ошибка сети" };
    }
}

// 3. Обновление интерфейса
async function updateUI() {
    const u = await api('/get_user', { user_id: uid });
    if (!u || u.error) return;

    // Обновляем все текстовые поля
    document.querySelectorAll('.val-strawberry').forEach(el => el.innerText = u.strawberry);
    document.querySelectorAll('.val-spins').forEach(el => el.innerText = u.spins);
    document.querySelectorAll('.val-level').forEach(el => el.innerText = u.click_level);
    
    const upBtn = document.getElementById('upgrade-btn');
    if (upBtn) {
        const nextCost = u.click_level >= 11 ? "МАКС" : UPGRADE_COSTS[u.click_level + 1][0];
        upBtn.innerText = `Улучшить (${nextCost})`;
    }

    // Профиль
    document.getElementById('profile-username').innerText = user?.first_name || u.username || "Игрок";
    if (user?.photo_url) document.getElementById('profile-avatar').src = user.photo_url;

    // Статистика
    const totalRed = (u.red_wins || 0) + (u.red_losses || 0);
    const wr = totalRed > 0 ? ((u.red_wins / totalRed) * 100).toFixed(1) : 0;
    document.getElementById('stat-winrate').innerText = wr + "%";
    
    const avg = u.red_count > 0 ? (u.total_pulls_for_avg_red / u.red_count).toFixed(1) : 0;
    document.getElementById('stat-avg-red').innerText = avg;
    
    document.getElementById('stat-spent-straw').innerText = u.spent_strawberry || 0;
    document.getElementById('stat-spent-spins').innerText = u.spent_spins || 0;

    // Если мы на вкладке "Дом", обновляем инвентарь
    if (document.getElementById('home-view').classList.contains('active')) {
        renderInventory();
    }
}

// 4. Логика вкладок
async function renderInventory() {
    const items = await api('/get_inventory', { user_id: uid });
    const container = document.getElementById('inventory-list');
    if (!container) return;
    container.innerHTML = "";
    if (items.length === 0) {
        container.innerHTML = "<p>У вас пока нет питомцев</p>";
        return;
    }
    items.forEach(item => {
        container.innerHTML += `
            <div class="pet-card">
                <img src="${item.pet_image}">
                <p><b>${item.pet_name}</b></p>
                <small>${item.pet_rarity}</small>
            </div>
        `;
    });
}

// 5. Действия
async function clickStrawberry() {
    const res = await api('/click', { user_id: uid });
    if (res.success) updateUI();
}

async function upgradeClicker() {
    const res = await api('/upgrade', { user_id: uid });
    if (res.success) updateUI();
    else alert(res.error);
}

function setBanner(id) {
    currentBanner = id;
    document.querySelectorAll('.banner-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('banner-'+id).classList.add('active');
}

async function buySpins(count) {
    const res = await api('/buy', { user_id: uid, count: count });
    if (res.success) updateUI();
    else alert(res.error);
}

async function spin(count) {
    const res = await api('/spin', { user_id: uid, count: count, banner_id: currentBanner });
    if (!res.success) return alert(res.error);

    const mainPet = res.pets[0];
    const overlay = document.getElementById('gacha-overlay');
    overlay.classList.remove('hidden');
    document.getElementById('res-card').classList.add('hidden');
    document.getElementById('anim-box').classList.remove('hidden');
    document.getElementById('gacha-gif').src = GIFS[mainPet.rarity] || GIFS.default;

    setTimeout(() => {
        document.getElementById('anim-box').classList.add('hidden');
        document.getElementById('res-card').classList.remove('hidden');
        document.getElementById('res-img').src = mainPet.image_url;
        document.getElementById('res-name').innerText = mainPet.name;
        document.getElementById('res-rarity').innerText = mainPet.rarity;
        updateUI();
    }, 4000); 
}

async function claimPromo() {
    const code = document.getElementById('promo-input').value;
    const res = await api('/claim_promo', { user_id: uid, code: code });
    alert(res.msg || res.error);
    updateUI();
}

async function openCollection() {
    const allPets = await api('/get_all_pets', {});
    const myItems = await api('/get_inventory', { user_id: uid });
    const myNames = myItems.map(i => i.pet_name);
    
    const grid = document.getElementById('collection-grid');
    grid.innerHTML = "";
    allPets.forEach(p => {
        const isHave = myNames.includes(p.name);
        grid.innerHTML += `
            <div class="coll-item ${isHave ? '' : 'gray'}">
                <img src="${p.image_url}">
                <p>${p.name}</p>
            </div>
        `;
    });
    document.getElementById('collection-overlay').classList.remove('hidden');
}

// Переключение видов
function showView(viewId) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(viewId).classList.add('active');
    
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    // Находим кнопку по тексту или ID
    event.currentTarget.classList.add('active');
    
    updateUI();
}

// Старт
document.addEventListener('DOMContentLoaded', () => {
    tg.expand();
    updateUI();
});
