const tg = window.Telegram.WebApp;
const uid = tg.initDataUnsafe.user?.id || 12345;

// --- ПОМОЩНИКИ ---
async function api(path, body) {
    const r = await fetch('/api' + path, {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body)
    });
    return r.json();
}

function showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(pageId).classList.add('active');
}

// --- ОСНОВНАЯ ЛОГИКА ---
async function updateUI() {
    const u = await api('/get_user', {user_id: uid});
    
    // Обновление валюты
    document.querySelectorAll('.strawberry-count').forEach(el => el.innerText = u.strawberry);
    document.querySelectorAll('.spins-count').forEach(el => el.innerText = u.spins);
    
    // Гаранты
    if (document.getElementById('p-red')) document.getElementById('p-red').innerText = u.pity_red;
    if (document.getElementById('p-ora')) document.getElementById('p-ora').innerText = u.pity_orange;
    if (document.getElementById('p-yel')) document.getElementById('p-yel').innerText = u.pity_yellow;
    if (document.getElementById('p-gre')) document.getElementById('p-gre').innerText = u.pity_green;
    if (document.getElementById('p-lbu')) document.getElementById('p-lbu').innerText = u.pity_lightblue;
    if (document.getElementById('p-blu')) document.getElementById('p-blu').innerText = u.pity_blue;
    
    // Уровень клика
    if (document.getElementById('click-lvl')) document.getElementById('click-lvl').innerText = u.click_level;
    const costs = {2:10, 3:40, 4:90, 5:160, 6:250, 7:360, 8:490, 9:640, 10:810, 11:4000};
    const upBtn = document.getElementById('upgrade-btn');
    if (upBtn) {
        if (u.click_level >= 11) upBtn.style.display = 'none';
        else upBtn.innerText = `Улучшить (${costs[u.click_level+1]} 🍓)`;
    }
}

async function collectStrawberry() {
    await api('/click', {user_id: uid});
}

async function spin(count) {
    const res = await api('/spin', {user_id: uid, count: count});
    if (res.success) {
        const names = res.pets.map(p => `${p.name} (${p.rarity})`).join(', ');
        document.getElementById('gacha-res').innerText = "Выпало: " + names;
        updateUI();
    } else alert(res.error);
}

async function buySpins(count) {
    const res = await api('/buy', {user_id: uid, count: count});
    if (res.success) updateUI(); else alert("Недостаточно клубники!");
}

async function upgrade() {
    const res = await api('/upgrade', {user_id: uid});
    if (res.success) updateUI(); else alert("Недостаточно клубники!");
}

// --- СТАРТ ---
document.addEventListener('DOMContentLoaded', () => {
    tg.expand();
    
    // Навигация
    document.getElementById('home-btn').onclick = () => showPage('home');
    document.getElementById('gacha-btn').onclick = () => showPage('gacha');
    document.getElementById('game-btn').onclick = () => showPage('game');
    document.getElementById('profile-btn').onclick = () => showPage('profile');

    // Кнопки
    if (document.getElementById('collect-btn')) document.getElementById('collect-btn').onclick = collectStrawberry;
    if (document.getElementById('upgrade-btn')) document.getElementById('upgrade-btn').onclick = upgrade;
    if (document.getElementById('spin-1')) document.getElementById('spin-1').onclick = () => spin(1);
    if (document.getElementById('spin-10')) document.getElementById('spin-10').onclick = () => spin(10);

    updateUI();
});

