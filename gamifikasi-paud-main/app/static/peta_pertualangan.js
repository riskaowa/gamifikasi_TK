const GAME_LIST = [
    { key: "huruf", routeAttr: "urlHuruf" },
    { key: "angka", routeAttr: "urlAngka" },
    { key: "warna", routeAttr: "urlWarna" }
];

const GAME_NAMES = {
    huruf: "Mengenal Huruf",
    angka: "Mengenal Angka",
    warna: "Mengenal Warna dan Bentuk Bangun Ruang"
};

let isPetaOpenNow = false;
let isVoiceEnabled = true;
let dailyGameStatus = {};
let adventureProgress = {};
let accessTimeStatus = {
    allowed_now: true,
    is_limited: false,
    start_time: "08:00",
    end_time: "22:00",
    message: "Klik ikon level untuk memulai permainan. Level akan terbuka setelah level sebelumnya selesai."
};

function buildClosedMessage() {
    if (accessTimeStatus && accessTimeStatus.message) {
        return accessTimeStatus.message;
    }
    return "Game hanya bisa dimainkan pada jam yang telah ditentukan oleh guru.";
}

function readInitialAccessStatusFromPage() {
    const page = document.getElementById("adventurePage");
    if (!page) {
        return;
    }

    accessTimeStatus.allowed_now = page.dataset.accessAllowed === "1";
    accessTimeStatus.is_limited = page.dataset.accessLimited === "1";
    accessTimeStatus.start_time = page.dataset.accessStart || "08:00";
    accessTimeStatus.end_time = page.dataset.accessEnd || "22:00";
    accessTimeStatus.message = page.dataset.accessMessage || buildClosedMessage();
}

async function fetchAccessTimeStatus() {
    try {
        const response = await fetch("/api/access-time-status");
        if (!response.ok) {
            return;
        }
        const data = await response.json();
        accessTimeStatus = {
            allowed_now: !!data.allowed_now,
            is_limited: !!data.is_limited,
            start_time: data.start_time || "08:00",
            end_time: data.end_time || "22:00",
            message: data.message || buildClosedMessage()
        };
    } catch (error) {
        console.warn("Gagal mengambil status jam akses:", error);
    }
}

async function fetchDailyGameStatus() {
    try {
        const response = await fetch("/api/game-daily-status");
        if (!response.ok) {
            return;
        }
        const data = await response.json();
        dailyGameStatus = data.games || {};
    } catch (error) {
        console.warn("Gagal mengambil status harian game:", error);
    }
}

async function fetchAdventureProgress() {
    try {
        const response = await fetch("/api/adventure-progress");
        if (!response.ok) {
            return;
        }
        const data = await response.json();
        adventureProgress = data.progress || {};
    } catch (error) {
        console.warn("Gagal mengambil progress petualangan:", error);
    }
}

function updateAccessInfo() {
    const helper = document.getElementById("petaAccessMessage");
    const mapShell = document.getElementById("mapShell");
    const overlay = document.getElementById("accessBlockOverlay");
    const scheduleTime = document.getElementById("blockScheduleTime");
    const blockHint = document.getElementById("blockHint");

    isPetaOpenNow = !accessTimeStatus.is_limited || accessTimeStatus.allowed_now;

    // Always update displayed schedule in overlay
    if (scheduleTime) {
        scheduleTime.textContent = `${accessTimeStatus.start_time} \u2013 ${accessTimeStatus.end_time}`;
    }

    if (isPetaOpenNow) {
        helper.textContent = "Klik ikon level untuk memulai permainan. Level akan terbuka setelah level sebelumnya selesai.";
        mapShell.classList.remove("access-closed");
        if (overlay) overlay.style.display = "none";
    } else {
        const closedMsg = buildClosedMessage();
        helper.textContent = closedMsg;
        mapShell.classList.add("access-closed");
        if (overlay) overlay.style.display = "flex";
        if (blockHint) {
            blockHint.textContent = `Harap tunggu hingga pukul ${accessTimeStatus.start_time}.`;
        }
    }
}

function getStatusText(status) {
    if (status === "selesai") {
        return '<span class="status-badge done">✅ Selesai</span>';
    }
    if (status === "sedang") {
        return '<span class="status-badge playing">🟡 Sedang dimainkan</span>';
    }
    if (status === "terkunci") {
        return '<span class="status-badge locked">🔒 Terkunci</span>';
    }
    return '<span class="status-badge pending">⚪ Belum dimainkan</span>';
}

function isGameUnlocked(gameKey) {
    const hurufDone = (adventureProgress.huruf?.status || "belum") === "selesai";
    const angkaDone = (adventureProgress.angka?.status || "belum") === "selesai";

    if (gameKey === "huruf") {
        return true;
    }
    if (gameKey === "angka") {
        return hurufDone;
    }
    if (gameKey === "warna") {
        return hurufDone && angkaDone;
    }
    return false;
}

function getLockedReason(gameKey) {
    if (gameKey === "angka") {
        return "Level ini akan terbuka setelah Mengenal Huruf selesai.";
    }
    if (gameKey === "warna") {
        return "Level ini akan terbuka setelah Mengenal Angka selesai.";
    }
    return "Level ini akan terbuka setelah level sebelumnya selesai.";
}

function updateProgress() {
    const doneCount = GAME_LIST.filter((game) => (adventureProgress[game.key]?.status || "belum") === "selesai").length;
    const percent = Math.floor((doneCount / GAME_LIST.length) * 100);
    document.getElementById("overallProgress").textContent = `${percent}%`;
    document.getElementById("starCount").textContent = String(doneCount);

    GAME_LIST.forEach((game) => {
        const status = adventureProgress[game.key]?.status || "belum";
        const perGame = status === "selesai" ? "100%" : status === "sedang" ? "50%" : "0%";
        const progressEl = document.getElementById(`progress-${game.key}`);
        progressEl.textContent = `Progress : ${perGame}`;
    });
}

function refreshGameCards() {
    GAME_LIST.forEach((game) => {
        const status = adventureProgress[game.key]?.status || "belum";
        const unlocked = isGameUnlocked(game.key);
        const displayStatus = unlocked ? status : "terkunci";
        const item = document.querySelector(`.game-item[data-game-key="${game.key}"]`) || document.querySelector(`.item-${game.key}`);
        const card = document.getElementById(`card-${game.key}`);
        const statusEl = document.getElementById(`status-${game.key}`);
        const todayInfo = dailyGameStatus[game.key] || { played_today: false, status_text: "Bisa dimainkan hari ini" };

        if (item) {
            item.classList.remove("status-belum", "status-sedang", "status-selesai", "status-terkunci");
            item.classList.add(`status-${displayStatus}`);
        }

        if (card) {
            card.classList.remove("status-belum", "status-sedang", "status-selesai", "status-terkunci");
            card.classList.add(`status-${displayStatus}`);
        }

        if (statusEl) {
            const lockedNotice = unlocked ? "" : ` <span class="status-badge">${getLockedReason(game.key)}</span>`;
            statusEl.innerHTML = `${getStatusText(displayStatus)} <span class="status-badge">${todayInfo.status_text}</span>${lockedNotice}`;
        }
    });

    updateProgress();
}

function getGameRoute(gameKey) {
    const page = document.getElementById("adventurePage");
    const conf = GAME_LIST.find((game) => game.key === gameKey);
    if (!conf) {
        return "";
    }
    return page.dataset[conf.routeAttr] || "";
}

function canPlayToday(gameKey) {
    const status = dailyGameStatus[gameKey];
    return !(status && status.played_today);
}

async function markGameInProgress(gameKey) {
    try {
        await fetch("/api/adventure-progress/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ game_key: gameKey })
        });
    } catch (error) {
        console.warn("Gagal menandai status sedang dimainkan:", error);
    }
}

async function handleGameAction(gameKey) {
    if (!isPetaOpenNow) {
        alert(buildClosedMessage());
        return;
    }

    if (!isGameUnlocked(gameKey)) {
        alert(getLockedReason(gameKey));
        return;
    }

    if (!canPlayToday(gameKey)) {
        alert("Game ini sudah dimainkan hari ini, silakan coba lagi besok.");
        return;
    }

    const route = getGameRoute(gameKey);
    if (!route) {
        return;
    }

    await markGameInProgress(gameKey);
    window.location.href = route;
}

function closeGameModal() {
    const modal = document.getElementById("game-access-modal");
    if (modal) modal.style.display = "none";
}

function showAccessInfoModal(gameKey) {
    const modal = document.getElementById("game-access-modal");
    if (!modal) {
        handleGameAction(gameKey);
        return;
    }

    const titleEl = document.getElementById("modal-game-title");
    const timeEl = document.getElementById("modal-access-time");
    const lockedMsg = document.getElementById("modal-locked-msg");
    const playedMsg = document.getElementById("modal-played-msg");
    const playBtn = document.getElementById("modal-play-btn");

    if (titleEl) titleEl.textContent = GAME_NAMES[gameKey] || gameKey;
    if (timeEl) timeEl.textContent = accessTimeStatus.start_time + " \u2013 " + accessTimeStatus.end_time;

    // Determine state
    const outsideHours = accessTimeStatus.is_limited && !accessTimeStatus.allowed_now;
    const alreadyPlayed = !canPlayToday(gameKey);
    const unlocked = isGameUnlocked(gameKey);
    const canPlay = unlocked && !outsideHours && !alreadyPlayed;

    if (lockedMsg) {
        if (outsideHours) {
            lockedMsg.textContent = "Level ini hanya bisa diakses pada jam " + accessTimeStatus.start_time + " \u2013 " + accessTimeStatus.end_time + ".";
            lockedMsg.style.display = "";
        } else if (!unlocked) {
            lockedMsg.textContent = getLockedReason(gameKey);
            lockedMsg.style.display = "";
        } else {
            lockedMsg.style.display = "none";
        }
    }
    if (playedMsg) {
        playedMsg.style.display = alreadyPlayed ? "" : "none";
    }

    if (playBtn) {
        if (canPlay) {
            playBtn.style.display = "";
            playBtn.disabled = false;
            playBtn.style.opacity = "1";
            playBtn.style.cursor = "pointer";
            // Replace onclick to avoid stale closures
            const newBtn = playBtn.cloneNode(true);
            playBtn.parentNode.replaceChild(newBtn, playBtn);
            newBtn.addEventListener("click", async () => {
                closeGameModal();
                await handleGameAction(gameKey);
            });
        } else {
            playBtn.style.display = "";
            playBtn.disabled = true;
            playBtn.style.opacity = "0.45";
            playBtn.style.cursor = "not-allowed";
        }
    }

    modal.style.display = "flex";
}

function getPlayableGameKey() {
    const notPlayed = GAME_LIST.find((game) => (adventureProgress[game.key]?.status || "belum") !== "selesai");
    return notPlayed ? notPlayed.key : null;
}

function bindGameInteractions() {
    document.querySelectorAll(".node-circle").forEach((button) => {
        button.addEventListener("click", () => {
            const gameKey = button.dataset.gameKey;
            showAccessInfoModal(gameKey);
        });
    });

    document.querySelectorAll(".game-card").forEach((card) => {
        card.addEventListener("click", () => {
            const gameKey = card.dataset.gameKey;
            showAccessInfoModal(gameKey);
        });
    });

    const closeBtn = document.getElementById("modal-close-btn");
    if (closeBtn) {
        closeBtn.addEventListener("click", closeGameModal);
    }

    const modal = document.getElementById("game-access-modal");
    if (modal) {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) closeGameModal();
        });
    }

    const startButton = document.getElementById("btnStartMain");
    if (!startButton) {
        return;
    }

    startButton.addEventListener("click", async () => {
        const gameKey = getPlayableGameKey();

        if (!gameKey) {
            alert("Semua game sudah selesai dimainkan");
            return;
        }

        await handleGameAction(gameKey);
    });
}

function speakMascot(text) {
    if (!isVoiceEnabled) {
        return;
    }

    if (!("speechSynthesis" in window)) {
        return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "id-ID";
    utterance.rate = 0.95;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
}

function initMascotAnimation() {
    const wrap = document.getElementById("mascotWrap");
    const container = document.getElementById("mascotAnimation");
    if (!wrap || !container) {
        return;
    }

    const animationUrl = container.dataset.animationUrl;
    if (!animationUrl || !window.lottie) {
        wrap.classList.add("fallback");
        return;
    }

    try {
        window.lottie.loadAnimation({
            container,
            renderer: "svg",
            loop: true,
            autoplay: true,
            path: animationUrl
        });
        wrap.classList.remove("fallback");
    } catch (error) {
        wrap.classList.add("fallback");
    }
}

function getMascotSpeechText() {
    if (!isPetaOpenNow) {
        return `Game bisa dimainkan mulai pukul ${accessTimeStatus.start_time}`;
    }
    return "Ayo silakan bermain";
}

function initMascot() {
    const replayButton = document.getElementById("replayVoice");
    const toggleButton = document.getElementById("toggleVoice");

    // Jangan putar suara mascot otomatis saat halaman dibuka.
    // Hanya bermain.mp3 yang akan diputar sebagai audio utama.

    replayButton.addEventListener("click", () => {
        speakMascot(getMascotSpeechText());
    });

    toggleButton.addEventListener("click", () => {
        isVoiceEnabled = !isVoiceEnabled;
        toggleButton.textContent = isVoiceEnabled ? "Suara ON" : "Suara OFF";
        toggleButton.title = isVoiceEnabled ? "Matikan suara" : "Aktifkan suara";

        if (!isVoiceEnabled && "speechSynthesis" in window) {
            window.speechSynthesis.cancel();
        }
    });
}

async function initAdventureMap() {
    readInitialAccessStatusFromPage();
    await fetchAccessTimeStatus();
    updateAccessInfo();
    await fetchAdventureProgress();
    await fetchDailyGameStatus();
    refreshGameCards();
    bindGameInteractions();
    initMascotAnimation();
    initMascot();

    // Poll setiap 30 detik agar perubahan guru langsung berlaku
    setInterval(async () => {
        await fetchAccessTimeStatus();
        updateAccessInfo();
    }, 30000);

    setInterval(async () => {
        await fetchAdventureProgress();
        await fetchDailyGameStatus();
        refreshGameCards();
    }, 30000);
}

document.addEventListener("DOMContentLoaded", initAdventureMap);
