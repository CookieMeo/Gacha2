document.addEventListener('DOMContentLoaded', () => {
    // --- Telegram WebApp Initialization ---
    Telegram.WebApp.ready();
    Telegram.WebApp.expand();
    if (Telegram.WebApp.initDataUnsafe && Telegram.WebApp.initDataUnsafe.user) {
        console.log('Telegram User Data:', Telegram.WebApp.initDataUnsafe.user);
    }

    // --- DOM Elements ---
    const strawberryCountElem = document.getElementById('strawberry-count');

    const homeSection = document.getElementById('home-section');
    const gachaSection = document.getElementById('gacha-section');
    const gameSection = document.getElementById('game-section');
    const profileSection = document.getElementById('profile-section');

    const navHomeBtn = document.getElementById('nav-home');
    const navGachaBtn = document.getElementById('nav-gacha');
    const navGameBtn = document.getElementById('nav-game');
    const navProfileBtn = document.getElementById('nav-profile');
    const navButtons = [navHomeBtn, navGachaBtn, navGameBtn, navProfileBtn];

    const animalsGrid = document.getElementById('animals-grid');
    const noAnimalsMessage = document.getElementById('no-animals-message');

    const gachaSpinnerContainer = document.getElementById('gacha-spinner-container');
    const gachaSpinner = document.getElementById('gacha-spinner');
    const gachaAnimalImage = document.getElementById('gacha-animal-image');
    const gachaAnimalName = document.getElementById('gacha-animal-name');
    const gachaAnimalRarity = document.getElementById('gacha-animal-rarity');
    const spin1Btn = document.getElementById('spin-1-btn');
    const spin10Btn = document.getElementById('spin-10-btn');
    const pityList = document.getElementById('pity-list');

    const strawberryImage = document.getElementById('strawberry-image');
    const clickFeedback = document.getElementById('click-feedback');
    const clickerLevelElem = document.getElementById('clicker-level');
    const strawberriesPerClickElem = document.getElementById('strawberries-per-click');
    const upgradeClickerBtn = document.getElementById('upgrade-clicker-btn');
    const upgradeCostInfo = document.getElementById('upgrade-cost-info');

    const profileAvatar = document.getElementById('profile-avatar');
    const profileNickname = document.getElementById('profile-nickname');
    const profileLuck = document.getElementById('profile-luck');
    const profileTotalPets = document.getElementById('profile-total-pets');
    const profileStrawberriesSpent = document.getElementById('profile-strawberries-spent');
    const profileTotalClicks = document.getElementById('profile-total-clicks');
    const promoCodeInput = document.getElementById('promo-code-input');
    const activatePromoBtn = document.getElementById('activate-promo-btn');
    const promoMessage = document.getElementById('promo-message');

    // --- Game Data & Configuration ---
    const RARITIES = {
        'красное': { chance: 0.005, name: 'Красное (Легендарное)', color: 'red', pity: 40 },
        'оранжевое': { chance: 0.015, name: 'Оранжевое (Эпическое)', color: 'orange', pity: 30 },
        'желтое': { chance: 0.03, name: 'Желтое (Редкое)', color: 'yellow', pity: 15 },
        'зеленое': { chance: 0.08, name: 'Зеленое (Необычное)', color: 'green', pity: 10 },
        'голубое': { chance: 0.15, name: 'Голубое (Особое)', color: 'cyan', pity: 5 },
        'синее': { chance: 0.25, name: 'Синее (Обычное+)', color: 'blue', pity: 3 },
        'фиолетовое': { chance: 0.46, name: 'Фиолетовое (Обычное)', color: 'violet', pity: 0 } // No explicit pity for common
    };
    const BANNER_ANIMAL_ID = 'dragon'; // ID баннерного животного
    const GACHA_COST_PER_SPIN = 100;

    const ANIMALS = [
        // Красное
        { id: 'dragon', name: 'Дракон', rarity: 'красное', image: 'c:\Users\Home\Desktop\Гачуля\webapp\assets\pets\dragon.png' },
        { id: 'spider', name: 'Паук', rarity: 'красное', image: 'c:\Users\Home\Desktop\Гачуля\webapp\assets\pets\spider.png' },
        // Оранжевое
        { id: 'shark', name: 'Акула', rarity: 'оранжевое', image: 'c:\Users\Home\Desktop\Гачуля\webapp\assets\pets\shark.png' },
        { id: 'bat', name: 'Летучая мышь', rarity: 'оранжевое', image: 'c:\Users\Home\Desktop\Гачуля\webapp\assets\pets\bat.png' },
        // Желтое
        { id: 'parrot', name: 'Попугай', rarity: 'желтое', image: 'c:\Users\Home\Desktop\Гачуля\webapp\assets\pets\parrot.png' },
        { id: 'snake', name: 'Змея', rarity: 'желтое', image: 'c:\Users\Home\Desktop\Гачуля\webapp\assets\pets\snake.png' },
        // Зеленое
        { id: 'elephant', name: 'Слон', rarity: 'зеленое', image: 'c:\Users\Home\Desktop\Гачуля\webapp\assets\pets\elephant.png' },
        { id: 'turtle', name: 'Черепаха', rarity: 'зеленое', image: 'c:\Users\Home\Desktop\Гачуля\webapp\assets\pets\turtle.png' },
        // Голубое
        { id: 'bunny', name: 'Кролик', rarity: 'голубое', image: 'c:\Users\Home\Desktop\Гачуля\webapp\assets\pets\bunny.png' },
        { id: 'snail', name: 'Улитка', rarity: 'голубое', image: 'c:\Users\Home\Desktop\Гачуля\webapp\assets\pets\snail.png' },
        // Синее
        { id: 'mouse', name: 'Мышь', rarity: 'синее', image: 'c:\Users\Home\Desktop\Гачуля\webapp\assets\pets\mouse.png' },
        { id: 'hamster', name: 'Хомяк', rarity: 'синее', image: 'c:\Users\Home\Desktop\Гачуля\webapp\assets\pets\hamster.png' },
        // Фиолетовое
        { id: 'cat', name: 'Кот', rarity: 'фиолетовое', image: 'c:\Users\Home\Desktop\Гачуля\webapp\assets\pets\cat.png' },
        { id: 'dog', name: 'Собака', rarity: 'фиолетовое', image: 'c:\Users\Home\Desktop\Гачуля\webapp\assets\pets\dog.png' }
    ];

    const CLICKER_UPGRADE_COSTS = [
        0, // Уровень 1 (бесплатно)
        10, // Уровень 2
        40, // Уровень 3
        90, // Уровень 4
        160, // Уровень 5
        250, // Уровень 6
        360, // Уровень 7
        490, // Уровень 8
        640, // Уровень 9
        810  // Уровень 10
    ];

    // Промокоды (В реальной аппке это будет на сервере)
    const PROMO_CODES = {
        "MEOW": { spins: 40, used: false, message: "" },
        "WELCOMEBONUS": { strawberries: 500, used: false, message: "Приветственный бонус 500 клубник!" },
        "FREESPIN": { spins: 1, used: false, message: "Бесплатная крутка получена!" },
        "LUCKY2026": { strawberries: 1000, used: false, message: "Бонус к удачному году: 1000 клубник!" },
    };


    // --- User Data (persisted with localStorage) ---
    let userData = {
        strawberries: 0,
        animalsOwned: [], // Array of animal objects
        clickerLevel: 1,
        pityCounters: {}, // { 'красное': 0, 'оранжевое': 0, ... }
        redGuaranteedBanner: true, // True if the next red guarantees banner animal
        stats: {
            totalClicks: 0,
            strawberriesSpent: 0,
            totalPets: 0,
            luckyPulls: 0, // Early pulls, not pity
            pityPulls: 0, // Pulls that activated pity
        },
        promoCodesUsed: {}, // { "CODE": true }
        userId: Telegram.WebApp.initDataUnsafe?.user?.id || 'guest_' + Math.random().toString(36).substring(2, 11), // Уникальный ID для сохранения
        userName: Telegram.WebApp.initDataUnsafe?.user?.first_name || 'Игрок',
        userAvatar: `https://api.adorable-avatars.com/avatars/100/${Telegram.WebApp.initDataUnsafe?.user?.id || 'guest'}.png` // Пример
    };

    // Initialize rarity pity counters
    for (const rarityKey in RARITIES) {
        userData.pityCounters[rarityKey] = 0;
    }
    
    // --- Functions for Data Management ---
    function saveUserData() {
        localStorage.setItem(`gachaAppUser_${userData.userId}`, JSON.stringify(userData));
    }

    function loadUserData() {
        const savedData = localStorage.getItem(`gachaAppUser_${userData.userId}`);
        if (savedData) {
            const parsedData = JSON.parse(savedData);
            // Merge loaded data, ensuring new fields are initialized if not present in old save
            userData = { ...userData, ...parsedData };
            // Ensure pityCounters has all current rarities, old saves might miss new ones
            for (const rarityKey in RARITIES) {
                if (userData.pityCounters[rarityKey] === undefined) {
                    userData.pityCounters[rarityKey] = 0;
                }
            }
            // Ensure redGuaranteedBanner is set correctly if missing
            if (userData.redGuaranteedBanner === undefined) {
                userData.redGuaranteedBanner = true;
            }
            // Ensure promoCodesUsed is an object
            if (typeof userData.promoCodesUsed !== 'object' || userData.promoCodesUsed === null) {
                userData.promoCodesUsed = {};
            }
        }
        updateUI();
    }

    function updateUI() {
        strawberryCountElem.textContent = `🍓 ${userData.strawberries}`;
        updateHomeSection();
        updateGameSection();
        updateProfileSection();
        updatePityDisplay();
    }

    function updateHomeSection() {
        animalsGrid.innerHTML = '';
        if (userData.animalsOwned.length === 0) {
            noAnimalsMessage.style.display = 'block';
        } else {
            noAnimalsMessage.style.display = 'none';
            // Сортировка по редкости
            const sortedAnimals = [...userData.animalsOwned].sort((a, b) => {
                const rarityOrder = ['красное', 'оранжевое', 'желтое', 'зеленое', 'голубое', 'синее', 'фиолетовое'];
                return rarityOrder.indexOf(a.rarity) - rarityOrder.indexOf(b.rarity);
            });

            sortedAnimals.forEach(animal => {
                const card = document.createElement('div');
                card.className = 'animal-card';
                card.innerHTML = `
                    <img src="${animal.image}" alt="${animal.name}">
                    <div class="name">${animal.name}</div>
                    <div class="rarity ${RARITIES[animal.rarity].color}">${RARITIES[animal.rarity].name}</div>
                `;
                animalsGrid.appendChild(card);
            });
        }
    }

    function updateGameSection() {
        clickerLevelElem.textContent = userData.clickerLevel;
        const strawberriesPerClick = userData.clickerLevel;
        strawberriesPerClickElem.textContent = strawberriesPerClick;

        const nextLevel = userData.clickerLevel + 1;
        if (nextLevel <= 10) {
            const cost = CLICKER_UPGRADE_COSTS[nextLevel - 1];
            upgradeCostInfo.textContent = `Следующий уровень: ${nextLevel} (+${nextLevel} 🍓 за клик), Стоимость: ${cost} 🍓`;
            upgradeClickerBtn.textContent = `Улучшить (${cost} 🍓)`;
            upgradeClickerBtn.disabled = userData.strawberries < cost;
        } else {
            upgradeCostInfo.textContent = 'Клубника прокачана до максимального уровня!';
            upgradeClickerBtn.textContent = 'Макс. уровень';
            upgradeClickerBtn.disabled = true;
        }
    }

    function updateProfileSection() {
        profileAvatar.src = Telegram.WebApp.initDataUnsafe?.user?.photo_url || userData.userAvatar;
        profileNickname.textContent = Telegram.WebApp.initDataUnsafe?.user?.first_name || userData.userName;

        const totalPulls = userData.stats.luckyPulls + userData.stats.pityPulls;
        const luckPercentage = totalPulls > 0 ? ((userData.stats.luckyPulls / totalPulls) * 100).toFixed(2) : 0;

        profileLuck.textContent = `${luckPercentage}%`;
        profileTotalPets.textContent = userData.animalsOwned.length;
        profileStrawberriesSpent.textContent = userData.stats.strawberriesSpent;
        profileTotalClicks.textContent = userData.stats.totalClicks;
    }

    function updatePityDisplay() {
        pityList.innerHTML = '';
        const rarityOrder = ['красное', 'оранжевое', 'желтое', 'зеленое', 'голубое', 'синее']; // Фиолетовое без пити

        rarityOrder.forEach(rarityKey => {
            const pityThreshold = RARITIES[rarityKey].pity;
            if (pityThreshold > 0) {
                const remaining = pityThreshold - userData.pityCounters[rarityKey];
                const listItem = document.createElement('li');
                listItem.textContent = `${RARITIES[rarityKey].name}: ${remaining <= 0 ? 'Гарант!' : `${remaining} круток`}`;
                if (remaining <= 0) {
                    listItem.style.backgroundColor = '#ffd700'; // Gold for guaranteed
                    listItem.style.color = '#333';
                }
                pityList.appendChild(listItem);
            }
        });
    }

    // --- Navigation ---
    function showSection(sectionId) {
        const sections = [homeSection, gachaSection, gameSection, profileSection];
        sections.forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(sectionId).classList.add('active');

        navButtons.forEach(button => {
            button.classList.remove('active');
        });
        document.getElementById(`nav-${sectionId.replace('-section', '')}`).classList.add('active');

        Telegram.WebApp.MainButton.hide(); // Hide main button by default for sections
    }

    // Функция для безопасного добавления клика
    function setupClick(id, callback) {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('click', callback);
        } else {
            console.warn(`Кнопка с id="${id}" не найдена в HTML!`);
        }
    }

    // Настраиваем навигацию
    setupClick('home-btn', () => showPage('home'));
    setupClick('gacha-btn', () => showPage('gacha'));
    setupClick('game-btn', () => showPage('game'));
    setupClick('profile-btn', () => showPage('profile'));


    // --- Game Logic: Clicker ---
    strawberryImage.addEventListener('click', () => {
        const strawberriesGained = userData.clickerLevel;
        userData.strawberries += strawberriesGained;
        userData.stats.totalClicks++;
        saveUserData();
        updateUI();

        // Click feedback animation
        const feedback = document.createElement('div');
        feedback.textContent = `+${strawberriesGained}`;
        feedback.className = 'click-feedback';
        const rect = strawberryImage.getBoundingClientRect();
        feedback.style.left = `${rect.left + rect.width / 2 + (Math.random() - 0.5) * 40}px`;
        feedback.style.top = `${rect.top + rect.height / 2 + (Math.random() - 0.5) * 40}px`;
        document.body.appendChild(feedback);
        feedback.addEventListener('animationend', () => feedback.remove());
    });

    upgradeClickerBtn.addEventListener('click', () => {
        const nextLevel = userData.clickerLevel + 1;
        if (nextLevel <= 10) {
            const cost = CLICKER_UPGRADE_COSTS[nextLevel - 1];
            if (userData.strawberries >= cost) {
                userData.strawberries -= cost;
                userData.clickerLevel = nextLevel;
                saveUserData();
                updateUI();
            } else {
                Telegram.WebApp.showAlert('Недостаточно клубники для улучшения!');
            }
        }
    });

    // --- Game Logic: Gacha ---
    function getRandomRarity() {
        let chosenRarity = null;
        let isPityPull = false;

        // Check for pity, from rarest to common
        const rarityOrder = ['красное', 'оранжевое', 'желтое', 'зеленое', 'голубое', 'синее'];
        for (const rarityKey of rarityOrder) {
            const pityThreshold = RARITIES[rarityKey].pity;
            if (pityThreshold > 0 && userData.pityCounters[rarityKey] >= pityThreshold) {
                chosenRarity = rarityKey;
                isPityPull = true;
                userData.stats.pityPulls++;
                break;
            }
        }

        // If no pity, roll based on chances
        if (!chosenRarity) {
            let rand = Math.random();
            let cumulativeChance = 0;
            for (const rarityKey in RARITIES) {
                cumulativeChance += RARITIES[rarityKey].chance;
                if (rand < cumulativeChance) {
                    chosenRarity = rarityKey;
                    userData.stats.luckyPulls++;
                    break;
                }
            }
        }
        return { rarity: chosenRarity, isPityPull: isPityPull };
    }

    function getAnimalByRarity(rarity) {
        const availableAnimals = ANIMALS.filter(animal => animal.rarity === rarity);
        if (rarity === 'красное') {
            const bannerAnimal = ANIMALS.find(animal => animal.id === BANNER_ANIMAL_ID);
            // Если гарантирован баннерный или это первая лега
            if (userData.redGuaranteedBanner) {
                userData.redGuaranteedBanner = false; // Следующая красная не гарантирует баннер
                return bannerAnimal;
            } else {
                // Выпала красная, но не баннер
                const otherRedAnimals = availableAnimals.filter(animal => animal.id !== BANNER_ANIMAL_ID);
                const chosen = otherRedAnimals[Math.floor(Math.random() * otherRedAnimals.length)];
                userData.redGuaranteedBanner = true; // Следующая красная будет гарантировать баннер
                return chosen;
            }
        } else {
            return availableAnimals[Math.floor(Math.random() * availableAnimals.length)];
        }
    }

    function resetPity(rolledRarity) {
        for (const rarityKey in RARITIES) {
            // Reset only for the rarity rolled, and all higher rarities
            // E.g., if you pull a red, all pity counters reset (red, orange, yellow, etc.)
            // If you pull an orange, orange pity and higher rarities (yellow, green, ...) reset
            if (RARITIES[rarityKey].chance <= RARITIES[rolledRarity].chance) {
                userData.pityCounters[rarityKey] = 0;
            } else {
                userData.pityCounters[rarityKey]++; // Increment lower rarity pity counters
            }
        }
    }


    async function spinGacha(numSpins) {
        const totalCost = numSpins * GACHA_COST_PER_SPIN;
        if (userData.strawberries < totalCost) {
            Telegram.WebApp.showAlert('Недостаточно клубники для крутки!');
            return;
        }

        spin1Btn.disabled = true;
        spin10Btn.disabled = true;
        userData.strawberries -= totalCost;
        userData.stats.strawberriesSpent += totalCost;

        const results = [];
        for (let i = 0; i < numSpins; i++) {
            const { rarity: rolledRarity, isPityPull } = getRandomRarity();
            const chosenAnimal = getAnimalByRarity(rolledRarity);
            
            // Increment all pity counters before resetting for the current pull
            for (const rarityKey in RARITIES) {
                userData.pityCounters[rarityKey]++;
            }

            // Reset pity logic
            resetPity(rolledRarity);

            userData.animalsOwned.push(chosenAnimal);
            userData.stats.totalPets++;
            results.push(chosenAnimal);
        }

        // Animation only for the last pulled animal (or single pull)
        const finalAnimal = results[results.length - 1];
        await animateGachaSpin(finalAnimal);

        saveUserData();
        updateUI();
        spin1Btn.disabled = false;
        spin10Btn.disabled = false;

        // For 10 pulls, might show a summary of all animals pulled
        if (numSpins > 1) {
             Telegram.WebApp.showAlert(`Вы выбили ${results.length} питомцев! Последний: ${finalAnimal.name} (${RARITIES[finalAnimal.rarity].name})`);
        }
    }

    // Function to get the target rotation for a rarity
    function getRotationForRarity(rarity) {
        const rarityAngles = {
            'фиолетовое': 0,
            'синее': 51.4,
            'голубое': 102.8,
            'зеленое': 154.2,
            'желтое': 205.6,
            'оранжевое': 257,
            'красное': 308.4
        };
        // We want the indicator to point *at* the segment.
        // The segments are rotated, so we need to calculate an appropriate stopping point.
        // A full circle is 360 degrees. 7 segments means 360/7 = ~51.4 degrees per segment.
        // Let's add multiple full rotations to make it spin
        const baseRotation = rarityAngles[rarity];
        return 360 * 5 + baseRotation + (Math.random() * 40 - 20); // 5 full spins + target + slight random jitter
    }

    async function animateGachaSpin(animal) {
        // Hide previous result
        gachaAnimalImage.style.display = 'none';
        gachaAnimalName.style.display = 'none';
        gachaAnimalRarity.style.display = 'none';
        
        gachaSpinner.style.transition = 'none'; // Reset transition instantly
        gachaSpinner.style.transform = 'rotate(0deg)'; // Start from 0

        await new Promise(resolve => setTimeout(resolve, 50)); // Small delay to apply reset

        const targetRotation = getRotationForRarity(animal.rarity);
        gachaSpinner.style.transition = 'transform 5s cubic-bezier(0.1, 0.7, 0.9, 1)';
        gachaSpinner.style.transform = `rotate(-${targetRotation}deg)`; // Spin counter-clockwise

        await new Promise(resolve => setTimeout(resolve, 5000)); // Wait for animation to complete

        // Display result
        gachaAnimalImage.src = animal.image;
        gachaAnimalImage.style.display = 'block';
        gachaAnimalName.textContent = animal.name;
        gachaAnimalName.style.display = 'block';
        gachaAnimalRarity.textContent = RARITIES[animal.rarity].name;
        gachaAnimalRarity.className = `rarity ${RARITIES[animal.rarity].color}`;
        gachaAnimalRarity.style.display = 'block';
    }


    spin1Btn.addEventListener('click', () => spinGacha(1));
    spin10Btn.addEventListener('click', () => spinGacha(10));

    // --- Promo Code Logic ---
    activatePromoBtn.addEventListener('click', () => {
        const code = promoCodeInput.value.trim().toUpperCase();
        if (!code) {
            promoMessage.textContent = 'Введите промокод.';
            promoMessage.style.color = 'orange';
            return;
        }

        if (userData.promoCodesUsed[code]) {
            promoMessage.textContent = 'Этот промокод уже был использован.';
            promoMessage.style.color = 'red';
            return;
        }

        const promo = PROMO_CODES[code];
        if (promo) {
            if (promo.strawberries) {
                userData.strawberries += promo.strawberries;
            }
            if (promo.spins) {
                // For simplicity, 1 free spin means 100 strawberries to spend.
                // Or you could make a separate gacha logic for free spins.
                // Let's just add equivalent strawberries for this demo.
                userData.strawberries += promo.spins * GACHA_COST_PER_SPIN;
            }
            userData.promoCodesUsed[code] = true;
            promoMessage.textContent = promo.message;
            promoMessage.style.color = 'green';
            saveUserData();
            updateUI();
        } else {
            promoMessage.textContent = 'Неверный промокод.';
            promoMessage.style.color = 'red';
        }
        promoCodeInput.value = '';
    });


    // --- Initialization ---
    loadUserData();
    showSection('home-section'); // Start on the home section
});


