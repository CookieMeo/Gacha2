const tg = window.Telegram.WebApp;
const uid = tg.initDataUnsafe.user?.id || 12345;

const UPGRADE_COSTS = {
    2: 10, 3: 40, 4: 90, 5: 160, 6: 250, 7: 360, 8: 490, 9: 640, 10: 810, 11: 4000
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

// Переименовали функцию в buy, чтобы HTML её видел
async function buy(count) {
    const res = await api('/buy', { user_id: uid, count: count });
    if (res.success) {
        updateUI();
    } else {
        alert("Недостаточно клубники!");
    }
}

async function spin(count) {
    const res = await api('/spin', { user_id: uid, count: count });
    if (res.success) {
        const names = res.pets.map(p => `${p.name} (${p.rarity})`).join(', ');
        document.getElementById('gacha-res').innerText = "Выпало: " + names;
        updateUI();
    } else alert(res.error);
}

function showPage(id) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(id).classList.add('active');
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

    // Привязка кнопок круток
    if (document.getElementById('spin-1')) document.getElementById('spin-1').onclick = () => spin(1);
    if (document.getElementById('spin-10')) document.getElementById('spin-10').onclick = () => spin(10);
    
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






