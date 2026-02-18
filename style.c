body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    background-color: var(--tg-theme-bg-color); /* Используем цвета Telegram */
    color: var(--tg-theme-text-color);
    display: flex;
    justify-content: center;
    align-items: flex-start; /* Align at the top */
    min-height: 100vh;
    padding-bottom: 80px; /* Space for fixed navigation */
    box-sizing: border-box;
}

.app-container {
    width: 100%;
    max-width: 600px;
    background-color: var(--tg-theme-secondary-bg-color);
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    padding: 20px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
}

h2 {
    color: var(--tg-theme-text-color);
    text-align: center;
    margin-bottom: 20px;
}

.screen {
    display: none;
    animation: fadeIn 0.3s ease-out;
}

.screen.active {
    display: block;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* --- Navigation --- */
.navigation-buttons {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    max-width: 600px; /* Same as app-container */
    margin: 0 auto;
    display: flex;
    justify-content: space-around;
    padding: 10px 0;
    background-color: var(--tg-theme-secondary-bg-color);
    border-top: 1px solid var(--tg-theme-hint-color);
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
    z-index: 1000;
}

.nav-btn {
    flex: 1;
    background: none;
    border: none;
    color: var(--tg-theme-hint-color);
    padding: 10px 5px;
    font-size: 14px;
    cursor: pointer;
    transition: color 0.2s ease, background-color 0.2s ease;
    border-radius: 5px;
}

.nav-btn:hover {
    color: var(--tg-theme-link-color);
}

.nav-btn.active {
    color: var(--tg-theme-button-color);
    background-color: var(--tg-theme-button-text-color);
    font-weight: bold;
}

/* --- General Buttons --- */
.btn {
    background-color: var(--tg-theme-button-color);
    color: var(--tg-theme-button-text-color);
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    margin-top: 10px;
    transition: background-color 0.2s ease;
    width: 100%;
    box-sizing: border-box;
}

.btn:hover:not(:disabled) {
    background-color: var(--tg-theme-link-color);
}

.btn:disabled {
    background-color: var(--tg-theme-hint-color);
    cursor: not-allowed;
    opacity: 0.7;
}

/* --- Home Screen (Pet Grid) --- */
.pet-grid {
    display: grid;
    grid-template-columns: 1fr 1fr; /* 2 pets per row */
    gap: 15px;
    margin-top: 20px;
}

.pet-card {
    background-color: var(--tg-theme-bg-color);
    border-radius: 8px;
    padding: 10px;
    text-align: center;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.pet-card img {
    width: 100px;
    height: 100px;
    object-fit: contain;
    margin-bottom: 5px;
}

.pet-card p {
    margin: 0;
    font-size: 14px;
}

.rarity-Красное { color: #FF0000; font-weight: bold; }
.rarity-Оранжевое { color: #FFA500; font-weight: bold; }
.rarity-Жёлтое { color: #FFFF00; font-weight: bold; }
.rarity-Зеленое { color: #00FF00; font-weight: bold; }
.rarity-Голубое { color: #00FFFF; font-weight: bold; }
.rarity-Синее { color: #0000FF; font-weight: bold; }
.rarity-Фиолетовое { color: #8A2BE2; font-weight: bold; }

/* --- Gacha Screen --- */
.gacha-area {
    position: relative;
    width: 100%;
    max-width: 300px; /* Adjust as needed */
    margin: 20px auto;
    aspect-ratio: 1 / 1; /* Make it square */
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: var(--tg-theme-bg-color);
    border-radius: 10px;
    overflow: hidden;
}

.roulette-gif {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block; /* Show by default, hide when result */
}

.gacha-result {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    display: none; /* Hide by default */
    z-index: 2;
    background-color: rgba(var(--tg-theme-secondary-bg-color-rgb), 0.9);
    border-radius: 10px;
    padding: 15px;
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
}

.gacha-result img {
    width: 150px;
    height: 150px;
    object-fit: contain;
    margin-bottom: 10px;
}
.gacha-result p {
    margin: 0;
    font-size: 16px;
}


.gacha-buttons {
    display: flex;
    gap: 10px;
    margin-top: 20px;
}

.gacha-buttons .btn {
    flex: 1;
}

.gacha-guarantees {
    margin-top: 30px;
    background-color: var(--tg-theme-bg-color);
    padding: 15px;
    border-radius: 8px;
}

.gacha-guarantees h3 {
    text-align: center;
    margin-top: 0;
    color: var(--tg-theme-text-color);
}

.gacha-guarantees ul {
    list-style: none;
    padding: 0;
    margin: 0;
    text-align: center;
}

.gacha-guarantees li {
    padding: 5px 0;
    font-size: 14px;
    color: var(--tg-theme-hint-color);
}

/* --- Game Screen (Clicker) --- */
.strawberry-clicker {
    position: relative;
    width: 200px;
    height: 200px;
    margin: 30px auto;
    cursor: pointer;
    text-align: center;
    user-select: none;
}

.strawberry-img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    transition: transform 0.1s ease;
}

.strawberry-img:active {
    transform: scale(0.2);
}

.clicker-info {
    text-align: center;
    margin-top: 20px;
}

.upgrade-btn {
    margin-top: 20px;
}

#click-feedback-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none; /* Make sure clicks go through to the strawberry */
}

.click-feedback {
    position: absolute;
    font-size: 1.5em;
    font-weight: bold;
    color: #FF69B4; /* Hot pink for strawberry */
    opacity: 0;
    animation: clickRiseFade 1s forwards;
    white-space: nowrap; /* Prevent line breaks */
}

@keyframes clickRiseFade {
    0% {
        transform: translateY(0) scale(1);
        opacity: 1;
    }
    100% {
        transform: translateY(-50px) scale(1.2);
        opacity: 0;
    }
}


/* --- Profile Screen --- */
.profile-info {
    text-align: center;
    margin-bottom: 30px;
    background-color: var(--tg-theme-bg-color);
    padding: 20px;
    border-radius: 8px;
}

.profile-avatar {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
    margin-bottom: 15px;
    border: 3px solid var(--tg-theme-link-color);
}

.profile-info p {
    margin: 5px 0;
    font-size: 15px;
}

.promocode-section {
    margin-top: 30px;
    text-align: center;
    background-color: var(--tg-theme-bg-color);
    padding: 20px;
    border-radius: 8px;
}

.promocode-section input {
    width: calc(100% - 20px);
    padding: 10px;
    margin-bottom: 10px;
    border: 1px solid var(--tg-theme-hint-color);
    border-radius: 5px;
    background-color: var(--tg-theme-secondary-bg-color);
    color: var(--tg-theme-text-color);
    box-sizing: border-box;
}

/* --- Utility --- */
.hidden {
    display: none !important;
}

.info-message {
    text-align: center;
    margin-top: 15px;
    padding: 10px;
    border-radius: 5px;
    background-color: var(--tg-theme-hint-color);
    color: var(--tg-theme-text-color);
    font-size: 14px;
}

.info-message.error {
    background-color: #ffcccc;
    color: #cc0000;
}

.info-message.success {
    background-color: #ccffcc;
    color: #006600;
}
