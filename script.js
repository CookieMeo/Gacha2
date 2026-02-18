const tg = window.Telegram.WebApp;

// --- DOM Elements ---
const screens = {
    home: document.getElementById('home-screen'),
    gacha: document.getElementById('gacha-screen'),
    game: document.getElementById('game-screen'),
    profile: document.getElementById('profile-screen')
};

const navButtons = document.querySelectorAll('.nav-btn');

// Home screen elements
const petGrid = document.getElementById('pet-grid');
const noPetsMessage = document.getElementById('no-pets-message');

// Gacha screen elements
const gachaStrawberryBalance = document.getElementById('gacha-strawberry-balance');
const rouletteGif = document.getElementById('roulette-gif');
const gachaResult = document.getElementById('gacha-result');
const spin1Btn = document.getElementById('spin-1-btn');
const spin10Btn = document.getElementById('spin-10-btn');
const gachaMessage = document.getElementById('gacha-message');
const guaranteeList = document.getElementById('guarantee-list');

// Game screen elements
const gameStrawberryBalance = document.getElementById('game-strawberry-balance');
const strawberryImg = document.getElementById('strawberry-img');
const clickFeedbackContainer = document.getElementById('click-feedback-container');
const clickerLevelSpan = document.getElementById('clicker-level');
const perClickAmountSpan = document.getElementById('per-click-amount');
const upgradeClickerBtn = document.getElementById('upgrade-clicker-btn');
const upgradeCostSpan = document.getElementById('upgrade-cost');
const upgradeMessage = document.getElementById('upgrade-message');

// Profile screen elements
const profileAvatar = document.getElementById('profile-avatar');
const profileUsername = document.getElementById('profile-username');
const profileTotalPets = document.getElementById('profile-total-pets');
const profileStrawberriesSpent = document.getElementById('profile-strawberries-spent');
const profileTotalClicks = document.getElementById('profile-total-clicks');
const promocodeInput = document.getElementById('promocode-input');
const applyPromocodeBtn = document.getElementById('apply-promocode-btn');
const promocodeMessage = document.getElementById('promocode-message');

// --- State Variables ---
let currentStrawberryBalance = 0;
let clickerLevel = 1;
let strawberriesPerClick = 1;
let nextUpgradeCost = 0;
let maxClickerLevel = 10; // Default, will be updated from backend

// --- Utility Functions ---

function showMessage(element, message, type = 'info', timeout = 3000) {
    element.textContent = message;
    element.className = `info-message ${type}`;
    element.classList.remove('hidden');
    setTimeout(() => {
        element.classList.add('hidden');
    }, timeout);
}

function updateStrawberryBalance(newBalance) {
    currentStrawberryBalance = newBalance;
    gachaStrawberryBalance.textContent = newBalance;
    gameStrawberryBalance.textContent = newBalance;
}

function showScreen(screenId) {
    // Hide all screens
    Object.values(screens).forEach(screen => screen.classList.add('hidden'));
    // Show the target screen
    screens[screenId].classList.remove('hidden');

    // Update navigation button active state
    navButtons.forEach(btn => {
        if (btn.dataset.target === screenId) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

async function sendDataToBackend(action, payload = {}) {
    const dataToSend = {
        action: action,
        user_id: tg.initDataUnsafe.user.id,
        ...payload
    };
    tg.sendData(JSON.stringify(dataToSend));
    // Telegram bot will receive this via update.web_app_data
}

async function fetchAndRenderUserData() {
    // Show loading indicator if needed
    
    await sendDataToBackend("get_user_data"); // Request user data
    // Response will be handled by tg.onEvent('onEvent') in script.js, specifically for 'web_app_data_received'
}


// --- Render Functions ---

function renderPets(pets) {
    petGrid.innerHTML = ''; // Clear previous pets
    if (pets && pets.length > 0) {
        noPetsMessage.classList.add('hidden');
        pets.forEach(pet => {
            const petCard = document.createElement('div');
            petCard.className = 'pet-card';
            petCard.innerHTML = `
                <img src="${pet.image_url}" alt="${pet.name}">
                <p><strong>${pet.name}</strong></p>
                <p class="rarity-${pet.rarity.replace(/ /g, '')}">${pet.rarity}</p>
            `;
            petGrid.appendChild(petCard);
        });
    } else {
        noPetsMessage.classList.remove('hidden');
    }
}

function renderGuarantees(guarantees) {
    guaranteeList.innerHTML = '';
    for (const rarity in guarantees) {
        const li = document.createElement('li');
        li.textContent = `До ${rarity}: ${guarantees[rarity]} круток`;
        if (guarantees[rarity] === "ГАРАНТ!") {
             li.textContent = `До ${rarity}: ГАРАНТ! (Следующая красная будет баннерной)`;
             li.style.color = '#FF0000'; // Make it red
        } else if (guarantees[rarity] <= 5 && guarantees[rarity] > 0) {
            li.style.color = '#FFA500'; // Orange for low count
        }
        guaranteeList.appendChild(li);
    }
}

function renderProfile(user, pets, clicksTotal, strawberriesSpent) {
    if (tg.initDataUnsafe.user.photo_url) {
        profileAvatar.src = tg.initDataUnsafe.user.photo_url;
        profileAvatar.classList.remove('hidden');
    } else {
        profileAvatar.classList.add('hidden');
    }
    profileUsername.textContent = user.username || tg.initDataUnsafe.user.first_name;
    profileTotalPets.textContent = pets.length;
    profileStrawberriesSpent.textContent = strawberriesSpent;
    profileTotalClicks.textContent = clicksTotal;
}

// --- Event Handlers ---

// Navigation buttons
navButtons.forEach(button => {
    button.addEventListener('click', () => {
        const targetScreen = button.dataset.target;
        showScreen(targetScreen);
        // Reload data for the active screen
        if (targetScreen === 'home-screen') {
            fetchAndRenderUserData(); // Refresh pets
        } else if (targetScreen === 'gacha-screen') {
            fetchAndRenderUserData(); // Refresh balance and guarantees
            gachaResult.innerHTML = '';
            gachaResult.classList.add('hidden');
            rouletteGif.classList.remove('hidden');
        } else if (targetScreen === 'game-screen') {
            fetchAndRenderUserData(); // Refresh balance and clicker info
        } else if (targetScreen === 'profile-screen') {
            fetchAndRenderUserData(); // Refresh profile stats
        }
    });
});

// Strawberry clicker
strawberryImg.addEventListener('click', () => {
    // Show "+X" feedback
    const feedback = document.createElement('div');
    feedback.textContent = `+${strawberriesPerClick}`;
    feedback.classList.add('click-feedback');

    // Random position around the strawberry
    const rect = strawberryImg.getBoundingClientRect();
    const x = Math.random() * (rect.width * 0.6) + rect.width * 0.2; // 20-80% width
    const y = Math.random() * (rect.height * 0.6) + rect.height * 0.2; // 20-80% height

    feedback.style.left = `${x}px`;
    feedback.style.top = `${y}px`;

    clickFeedbackContainer.appendChild(feedback);

    // Remove feedback after animation
    feedback.addEventListener('animationend', () => {
        feedback.remove();
    });

    sendDataToBackend("click_strawberry");
});

// Upgrade clicker
upgradeClickerBtn.addEventListener('click', () => {
    if (currentStrawberryBalance < nextUpgradeCost) {
        showMessage(upgradeMessage, "Недостаточно клубники для улучшения!", 'error');
        return;
    }
    upgradeClickerBtn.disabled = true;
    sendDataToBackend("upgrade_clicker");
});

// Gacha spin buttons
spin1Btn.addEventListener('click', () => spinGacha(1));
spin10Btn.addEventListener('click', () => spinGacha(10));

async function spinGacha(numSpins) {
    if (currentStrawberryBalance < numSpins * 100) {
        showMessage(gachaMessage, "Недостаточно клубники для крутки!", 'error');
        return;
    }

    // Disable buttons during spin
    spin1Btn.disabled = true;
    spin10Btn.disabled = true;

    // Show roulette GIF and hide previous result
    rouletteGif.classList.remove('hidden');
    gachaResult.classList.add('hidden');
    gachaMessage.classList.add('hidden');

    // Simulate 5-second spin
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Send spin request to backend
    await sendDataToBackend("spin_gacha", { num_spins: numSpins });
}

// Promocode button
applyPromocodeBtn.addEventListener('click', () => {
    const code = promocodeInput.value.trim();
    if (code) {
        applyPromocodeBtn.disabled = true;
        sendDataToBackend("apply_promocode", { code: code });
    } else {
        showMessage(promocodeMessage, "Пожалуйста, введите промокод.", 'error');
    }
});

// --- Telegram WebApp Event Listener ---
tg.onEvent('web_app_data_received', (event) => {
    const data = JSON.parse(event.data);
    
    if (data.error) {
        // Handle errors from any action
        showMessage(gachaMessage, data.error, 'error');
        showMessage(upgradeMessage, data.error, 'error');
        showMessage(promocodeMessage, data.error, 'error');
    } else if (data.user) { // Initial user data fetch
        updateStrawberryBalance(data.user.strawberry_balance);
        clickerLevel = data.user.clicker_level;
        strawberriesPerClick = data.clicker_info.per_click;
        nextUpgradeCost = data.next_clicker_upgrade_cost;
        maxClickerLevel = data.max_clicker_level;

        // Update Home screen
        renderPets(data.pets);

        // Update Game screen
        clickerLevelSpan.textContent = clickerLevel;
        perClickAmountSpan.textContent = strawberriesPerClick;
        if (clickerLevel >= maxClickerLevel) {
            upgradeClickerBtn.disabled = true;
            upgradeCostSpan.textContent = "МАКС";
            showMessage(upgradeMessage, "Достигнут максимальный уровень кликера!", 'info');
        } else {
            upgradeClickerBtn.disabled = false;
            upgradeCostSpan.textContent = nextUpgradeCost;
        }

        // Update Profile screen
        const totalStrawberriesSpent = data.user.spins_total * 100; // Assuming 1 spin = 100 str
        renderProfile(data.user, data.pets, data.user.clicks_total, totalStrawberriesSpent);

        // Update Gacha screen guarantees (after user data is loaded)
        // We need specific next guarantee data, might need another request or calculate on backend
        // For now, these will be updated after an actual spin
        if (data.user_stats) { // if this data is present in the initial user_data response
             const nextGuarantees = calculateNextGuaranteesClientSide(data.user_stats);
             renderGuarantees(nextGuarantees);
        }

    } else if (data.new_balance !== undefined && data.strawberries_gained !== undefined) { // Clicker update
        updateStrawberryBalance(data.new_balance);
        // `+X` animation is already handled on frontend click
    } else if (data.new_level !== undefined) { // Clicker upgrade update
        updateStrawberryBalance(data.new_balance);
        clickerLevel = data.new_level;
        strawberriesPerClick = data.strawberries_per_click;
        nextUpgradeCost = data.next_level_cost;

        clickerLevelSpan.textContent = clickerLevel;
        perClickAmountSpan.textContent = strawberriesPerClick;
        if (clickerLevel >= maxClickerLevel) {
            upgradeClickerBtn.disabled = true;
            upgradeCostSpan.textContent = "МАКС";
            showMessage(upgradeMessage, "Достигнут максимальный уровень кликера!", 'info');
        } else {
            upgradeClickerBtn.disabled = false;
            upgradeCostSpan.textContent = nextUpgradeCost;
        }
        showMessage(upgradeMessage, `Кликер улучшен до ${clickerLevel} уровня!`, 'success');
        upgradeClickerBtn.disabled = false;
    } else if (data.pets_obtained) { // Gacha spin result
        updateStrawberryBalance(data.new_balance);

        // Hide GIF, show result
        rouletteGif.classList.add('hidden');
        gachaResult.classList.remove('hidden');

        let resultHTML = '';
        data.pets_obtained.forEach(pet => {
            resultHTML += `
                <img src="${pet.image_url}" alt="${pet.name}">
                <p>Вы получили: <strong>${pet.name}</strong></p>
                <p class="rarity-${pet.rarity.replace(/ /g, '')}">${pet.rarity}</p>
            `;
        });
        gachaResult.innerHTML = resultHTML;
        
        // Update guarantees
        renderGuarantees(data.next_guarantees);
        
        // Update profile stats
        profileTotalPets.textContent = parseInt(profileTotalPets.textContent) + data.pets_obtained.length;
        profileStrawberriesSpent.textContent = parseInt(profileStrawberriesSpent.textContent) + (data.pets_obtained.length * 100);

        // Re-enable buttons
        spin1Btn.disabled = false;
        spin10Btn.disabled = false;
        showMessage(gachaMessage, `Поздравляем с новой добычей!`, 'success');
        fetchAndRenderUserData(); // Refresh home screen to show new pets

    } else if (data.success && data.message) { // Promocode applied
        showMessage(promocodeMessage, data.message, 'success');
        promocodeInput.value = '';
        updateStrawberryBalance(data.new_balance);
        applyPromocodeBtn.disabled = false;
    } else if (data.error) { // Generic error from any action
        showMessage(gachaMessage, data.error, 'error'); // Fallback for Gacha
        showMessage(upgradeMessage, data.error, 'error'); // Fallback for Game
        showMessage(promocodeMessage, data.error, 'error'); // Promocode specific error
        spin1Btn.disabled = false;
        spin10Btn.disabled = false;
        upgradeClickerBtn.disabled = false;
        applyPromocodeBtn.disabled = false;
    }
});


// Helper to calculate guarantees client-side if initial data contains pity counters
function calculateNextGuaranteesClientSide(userStats) {
    const GATCHA_GUARANTEES = {
        "Красное": 40, "Оранжевое": 30, "Жёлтое": 15, "Зеленое": 10,
        "Голубое": 5, "Синее": 3
    };
    const nextGuarantees = {};

    nextGuarantees["Красное"] = Math.max(0, GATCHA_GUARANTEES["Красное"] - userStats.pity_red);
    nextGuarantees["Оранжевое"] = Math.max(0, GATCHA_GUARANTEES["Оранжевое"] - userStats.pity_orange);
    nextGuarantees["Жёлтое"] = Math.max(0, GATCHA_GUARANTEES["Жёлтое"] - userStats.pity_yellow);
    nextGuarantees["Зеленое"] = Math.max(0, GATCHA_GUARANTEES["Зеленое"] - userStats.pity_green);
    nextGuarantees["Голубое"] = Math.max(0, GATCHA_GUARANTEES["Голубое"] - userStats.pity_lightblue);
    nextGuarantees["Синее"] = Math.max(0, GATCHA_GUARANTEES["Синее"] - userStats.pity_blue);

    if (userStats.banner_pity_hard === 1) {
        nextGuarantees["Красное (баннер)"] = "ГАРАНТ!";
    } else {
        nextGuarantees["Красное (до 50/50)"] = GATCHA_GUARANTEES["Красное"] - userStats.banner_pity_soft;
    }
    return nextGuarantees;
}


// --- Initialization ---
tg.ready();
tg.expand(); // Expand Mini App to full screen

// Get the initial page from URL parameters
const urlParams = new URLSearchParams(window.location.search);
const initialPage = urlParams.get('page');

if (initialPage && screens[initialPage]) {
    showScreen(initialPage + '-screen');
} else {
    showScreen('home-screen'); // Default to home
}

fetchAndRenderUserData(); // Initial data load for the displayed screen

