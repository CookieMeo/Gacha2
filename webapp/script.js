const tg = window.Telegram.WebApp;
const uid = tg.initDataUnsafe.user?.id || 12345;

// --- ПОМОЩНИКИ ---
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



function showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(pageId).classList.add('active');
}

// --- ОСНОВНАЯ ЛОГИКА ---
async function updateUI() {
    console.log("Обновление интерфейса...");
    const u = await api('/get_user', { user_id: uid });
    if (!u) {
        console.error("Пользователь не получен!");
        return;
    }

    // Безопасное обновление текста по ID
    const setText = (id, text) => {
        const el = document.getElementById(id);
        if (el) el.innerText = text;
    };

    // Обновляем клубнику и уровень
    setText('straw-count', u.strawberry);
    setText('lvl-txt', "Уровень " + u.click_level);
    
    // Обновляем счетчики в гаче (если они есть)
    setText('p-red', u.pity_red);
    setText('p-ora', u.pity_orange);
    setText('p-yel', u.pity_yellow);
    setText('p-gre', u.pity_green);
    setText('p-lbu', u.pity_lightblue);
    setText('p-blu', u.pity_blue);
    
    // Кнопка улучшения
    const costs = {2:10, 3:40, 4:90, 5:160, 6:250, 7:360, 8:490, 9:640, 10:810, 11:4000};
    const upBtn = document.getElementById('up-btn');
    if (upBtn) {
        if (u.click_level >= 11) {
            upBtn.style.display = 'none';
        } else {
            const nextCost = costs[u.click_level + 1] || 0;
            upBtn.innerText = `Улучшить (${nextCost} 🍓)`;
        }
    }
    console.log("Данные обновлены: ", u.strawberry, "🍓");
}

async function collectStrawberry() {
    console.log("Клик!");
    const res = await api('/click', { user_id: uid });
    if (res.success) {
        updateUI(); // Принудительно обновляем экран
    }
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

    const strawBtn = document.getElementById('strawberry-btn');
    if (strawBtn) {
        strawBtn.onclick = collectStrawberry;
        console.log("Кнопка клубники готова");
    }

    // Привязка к кнопке улучшения
    const upBtn = document.getElementById('up-btn');
    if (upBtn) {
        upBtn.onclick = async () => {
            const res = await api('/upgrade', { user_id: uid });
            if (res.success) updateUI();
            else alert("Недостаточно клубники!");
        };
    }
    
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




