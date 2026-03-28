/* Sahayak AI — Frontend Logic */
/* Uses textContent everywhere, never innerHTML */

"use strict";

const analyzeBtn = document.getElementById("analyze-btn");
const btnText = document.getElementById("btn-text");
const textarea = document.getElementById("emergency-input");
const loadingDiv = document.getElementById("loading");
const loadingText = document.getElementById("loading-text");
const errorDiv = document.getElementById("error-msg");
const resultCard = document.getElementById("result-card");
const historySection = document.getElementById("history-section");
const historyList = document.getElementById("history-list");

// Chat UI elements
const chatInput = document.getElementById("chat-input");
const chatSendBtn = document.getElementById("chat-send-btn");
const chatHistory = document.getElementById("chat-history");

// Global context
let currentResultId = null;
let currentTTSData = null; // Store for TTS
let loadingInterval = null;
let lastKnownLocation = "Unknown";

// Loading stages to cycle through
const loadingStages = [
    "Understanding situation...",
    "Classifying emergency level...",
    "Finding specific action plans...",
    "Refining recommendations...",
    "Checking quality and facts...",
    "Finalizing response..."
];

// Theme toggle
const themeToggle = document.getElementById("theme-toggle");
themeToggle.addEventListener("click", () => {
    const body = document.body;
    body.classList.toggle("light-theme");
    const isLight = body.classList.contains("light-theme");
    themeToggle.textContent = isLight ? "🌙 Dark Mode" : "☀️ Light Mode";
});

// Templates setup
const templateBtns = document.querySelectorAll(".template-btn");
templateBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        textarea.value = btn.getAttribute("data-text");
        textarea.focus();
        // Optionally animate or trigger analyze Emergency directly
    });
});

/**
 * Main function — analyze the emergency input.
 */
async function analyzeEmergency() {
    const text = textarea.value.trim();

    // Validate input
    if (!text) {
        showError("Please describe an emergency situation before analyzing.");
        return;
    }
    if (text.length > 5000) {
        showError("Input is too long. Please restrict to 5000 characters.");
        return;
    }
    const injectPatterns = /ignore\s+(all\s+)?(previous\s+)?instructions|you\s+are\s+now|system\s+prompt|bypass\s+rules|DAN\s+mode/i;
    if (injectPatterns.test(text)) {
        showError("Input blocked: Security violation. Please state your real emergency.");
        return;
    }

    // Set loading state
    hideError();
    resultCard.hidden = true;
    loadingDiv.style.display = "flex";
    analyzeBtn.disabled = true;
    btnText.textContent = "Analyzing...";

    // Start cycling loading text
    let stageIdx = 0;
    loadingText.textContent = loadingStages[0];
    loadingInterval = setInterval(() => {
        stageIdx = (stageIdx + 1) % loadingStages.length;
        loadingText.getContext = loadingStages[stageIdx];
        loadingText.textContent = loadingStages[stageIdx];
    }, 4000); // Change text every 4 seconds

    // Grab location automatically for regional contacts
    const getLoc = () => new Promise((resolve) => {
        if (!navigator.geolocation) return resolve("Unknown");
        navigator.geolocation.getCurrentPosition(
            pos => resolve(`Lat: ${pos.coords.latitude}, Lng: ${pos.coords.longitude}`),
            err => resolve("Unknown"),
            { timeout: 5000 }
        );
    });

    try {
        const userLoc = await getLoc();
        lastKnownLocation = userLoc;

        const response = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ input: text, location: userLoc }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const detail = errorData.detail || errorData.error || `Error ${response.status}`;
            throw new Error(detail);
        }

        const data = await response.json();
        renderResult(data);
    } catch (err) {
        showError("Analysis failed: " + err.message);
    } finally {
        if (loadingInterval) clearInterval(loadingInterval);
        loadingDiv.style.display = "none";
        analyzeBtn.disabled = false;
        btnText.textContent = "Analyze Emergency";
    }
}

/**
 * Render the triage result card using textContent only (never innerHTML).
 */
function renderResult(data) {
    // Store result ID for context
    currentResultId = data.result_id || null;
    currentTTSData = data; // Cache for reading aloud
    
    // Clear old chat history when loading a new report
    while (chatHistory.firstChild) {
        chatHistory.removeChild(chatHistory.firstChild);
    }
    chatInput.value = "";
    // Severity badge
    const severityBadge = document.getElementById("severity-badge");
    severityBadge.textContent = (data.severity || "unknown").toUpperCase();
    severityBadge.className = "severity-badge " + (data.severity || "medium");

    // Confidence badge
    const confidenceBadge = document.getElementById("confidence-badge");
    confidenceBadge.textContent = "Confidence: " + (data.confidence || "medium");

    // Language badge — show if Google Translate was used
    const langBadge = document.getElementById("lang-badge");
    const LANG_NAMES = { hi: "Hindi", te: "Telugu", kn: "Kannada", ta: "Tamil", bn: "Bengali", mr: "Marathi", gu: "Gujarati", pa: "Punjabi" };
    const detectedLang = data.detected_language || "en";
    if (detectedLang !== "en") {
        const langName = LANG_NAMES[detectedLang] || detectedLang.toUpperCase();
        langBadge.textContent = "🌐 Translated from " + langName + " via Google Translate";
        langBadge.hidden = false;
    } else {
        langBadge.hidden = true;
    }

    // Reasoning
    const reasoningDiv = document.getElementById("result-reasoning");
    if (data.reasoning) {
        reasoningDiv.textContent = "🧠 " + data.reasoning;
        reasoningDiv.hidden = false;
    } else {
        reasoningDiv.hidden = true;
    }

    // Situation
    document.getElementById("result-situation").textContent = data.situation || "No situation details available";

    // Category and priority meta tags
    document.getElementById("result-category").textContent = "Category: " + (data.category || "other");
    document.getElementById("result-priority").textContent = "Priority: " + (data.priority || "urgent");

    // Actions list — build with DOM methods
    const actionsList = document.getElementById("result-actions");
    // Clear existing children
    while (actionsList.firstChild) {
        actionsList.removeChild(actionsList.firstChild);
    }
    const actions = data.actions || [];
    actions.forEach(function (action) {
        const li = document.createElement("li");
        li.textContent = action;
        actionsList.appendChild(li);
    });

    // Contacts — build with DOM methods
    const contactsGrid = document.getElementById("result-contacts");
    while (contactsGrid.firstChild) {
        contactsGrid.removeChild(contactsGrid.firstChild);
    }
    const contacts = data.contacts || [];
    contacts.forEach(function (contact) {
        const chip = document.createElement("a");
        chip.className = "contact-chip";
        chip.href = "tel:" + (contact.number || "");
        chip.setAttribute("aria-label", "Call " + (contact.name || "Emergency"));

        const nameSpan = document.createElement("span");
        nameSpan.textContent = contact.name || "Emergency";

        const numSpan = document.createElement("span");
        numSpan.className = "contact-number";
        numSpan.textContent = contact.number || "";

        chip.appendChild(nameSpan);
        chip.appendChild(numSpan);
        contactsGrid.appendChild(chip);
    });

    // WhatsApp SOS Generator
    const waChip = document.createElement("a");
    waChip.className = "contact-chip";
    waChip.style.background = "#25D366"; // WhatsApp Green
    waChip.style.color = "white";
    waChip.href = `https://wa.me/?text=🚨%20SOS!%20Emergency:%20${encodeURIComponent(data.category)}.%20Location:%20${encodeURIComponent(lastKnownLocation)}.%20Please%20send%20help!`;
    waChip.target = "_blank";
    
    const waName = document.createElement("span");
    waName.textContent = "WhatsApp SOS";
    const waIcon = document.createElement("span");
    waIcon.textContent = "🚨 Send";
    
    waChip.appendChild(waName);
    waChip.appendChild(waIcon);
    contactsGrid.appendChild(waChip);

    // Show the card
    resultCard.hidden = false;
    resultCard.focus();
}

/**
 * Show error message in the alert region.
 */
function showError(message) {
    errorDiv.textContent = message;
    errorDiv.hidden = false;
}

/**
 * Hide the error message.
 */
function hideError() {
    errorDiv.hidden = true;
    errorDiv.textContent = "";
}

/**
 * Load and render recent analysis history.
 */
async function loadHistory() {
    try {
        const response = await fetch("/history");
        if (!response.ok) return;
        const data = await response.json();
        const results = data.results || [];
        if (results.length === 0) return;

        while (historyList.firstChild) {
            historyList.removeChild(historyList.firstChild);
        }

        results.slice(0, 5).forEach(function (item) {
            const div = document.createElement("div");
            div.className = "history-item";

            const sitSpan = document.createElement("span");
            sitSpan.className = "history-situation";
            sitSpan.textContent = item.situation || "Unknown situation";

            const sevSpan = document.createElement("span");
            sevSpan.className = "severity-badge " + (item.severity || "medium");
            sevSpan.textContent = (item.severity || "medium").toUpperCase();

            div.appendChild(sitSpan);
            div.appendChild(sevSpan);
            historyList.appendChild(div);
        });

        historySection.hidden = false;
    } catch (err) {
        // Silently ignore history load errors
    }
}

/**
 * Append a chat bubble to the UI.
 */
function appendChatBubble(text, role) {
    const bubble = document.createElement("div");
    bubble.className = "chat-bubble " + role;
    bubble.textContent = text;
    chatHistory.appendChild(bubble);
    // Auto scroll bottom
    bubble.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Handle sending a follow-up chat message.
 */
async function sendChatMessage() {
    if (!currentResultId) return;
    const text = chatInput.value.trim();
    if (!text) return;
    if (text.length > 1000) {
        alert("Question too long. Max 1000 characters.");
        return;
    }
    const injectPatterns = /ignore\s+(all\s+)?(previous\s+)?instructions|you\s+are\s+now|system\s+prompt|bypass\s+rules|DAN\s+mode/i;
    if (injectPatterns.test(text)) {
        alert("Message blocked: Security violation.");
        return;
    }

    appendChatBubble(text, "user");
    chatInput.value = "";
    chatInput.disabled = true;
    chatSendBtn.disabled = true;

    try {
        const response = await fetch("/analyze/" + currentResultId + "/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: text }),
        });

        if (!response.ok) {
            throw new Error("Chat request failed");
        }
        
        const data = await response.json();
        appendChatBubble(data.answer, "ai");
    } catch (err) {
        appendChatBubble("❌ Error: " + err.message, "ai");
    } finally {
        chatInput.disabled = false;
        chatSendBtn.disabled = false;
        chatInput.focus();
    }
}

// Event listeners
analyzeBtn.addEventListener("click", analyzeEmergency);

chatSendBtn.addEventListener("click", sendChatMessage);
chatInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage();
    }
});

textarea.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        analyzeEmergency();
    }
});

// Load history on page load
document.addEventListener("DOMContentLoaded", loadHistory);

// TTS logic
const ttsBtn = document.getElementById("tts-btn");
if (ttsBtn) {
    ttsBtn.addEventListener("click", () => {
        if (!currentTTSData || !window.speechSynthesis) return;

        // Cancel any ongoing speech
        window.speechSynthesis.cancel();

        const textToRead = "Emergency Category: " + (currentTTSData.category||"") + ". Priority: " + (currentTTSData.priority||"") + ". " +
        "Actions: " + (currentTTSData.actions ? currentTTSData.actions.join('. ') : '');

        const utterance = new SpeechSynthesisUtterance(textToRead);
        utterance.rate = 1.0;
        window.speechSynthesis.speak(utterance);
    });
}

// Ensure speech stops if page is unloaded
window.addEventListener("beforeunload", () => {
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }
});
