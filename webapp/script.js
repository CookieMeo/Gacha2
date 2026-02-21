const tg = window.Telegram.WebApp;
const uid = tg.initDataUnsafe.user?.id || 12345;

// Таблица цен для уровней (согласно твоим правилам)
const UPGRADE_COSTS = {
    2: 10,
    3: 40,
    4: 90,
    5: 160,
    6: 250,
    7: 360,
    8: 490,
    9: 640,
    10: 810,
    11: 4000
};

async function api(path, body) {
    try {
        const r = await fetch('/api' + path, {
            method: 'POST', 
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        });
        return await r.json();
    } catch (e) {
        console.error("Ошибка API:", e);
        return { success: false };
    }
}

async function updateUI() {
    console.log("Обновление интерфейса...");
    const u = await api('/get_user', { user_id: uid });
    if (!u) return;

    // 1. Обновляем счетчик клубники (id="straw-count")
    const strawEl = document.getElementById('straw-count');
    if (strawEl) strawEl.innerText = u.strawberry;

    // 2. Обновляем заголовок уровня (id="lvl-display")
    const lvlEl = document.getElementById('lvl-display');
    if (lvlEl) lvlEl.innerText = "Уровень " + u.click_level;

    // 3. Обновляем кнопку улучшения (id="upgrade-btn")
    const upBtn = document.getElementById('upgrade-btn');
    if (upBtn) {
        const nextLevel = u.click_level + 1;
        const cost = UPGRADE_COSTS[nextLevel];

        if (cost !== undefined) {
            upBtn.innerText = `Улучшить (${cost} 🍓)`;
            upBtn.style.display = 'inline-block'; // Показываем кнопку
        } else {
            // Если уровня нет в списке (максимальный уровень)
            upBtn.innerText = "Макс. уровень";
            upBtn.disabled = true; 
        }
    }
}

// Клик по клубнике
async function collectStrawberry() {
    const res = await api('/click', { user_id: uid });
    if (res.success) {
        updateUI();
    }
}

// Улучшение кликера
async function upgradeClicker() {
    const res = await api('/upgrade', { user_id: uid });
    if (res.success) {
        updateUI();
    } else {
        alert("Недостаточно клубники!");
    }
}

function showPage(id) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const target = document.getElementById(id);
    if (target) target.classList.add('active');
}

document.addEventListener('DOMContentLoaded', () => {
    tg.expand();
    
    // Привязываем кнопки по их правильным ID из твоего HTML
    const collectBtn = document.getElementById('collect-btn');
    if (collectBtn) collectBtn.onclick = collectStrawberry;

    const upgradeBtn = document.getElementById('upgrade-btn');
    if (upgradeBtn) upgradeBtn.onclick = upgradeClicker;
    
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





