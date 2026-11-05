const form = document.querySelector("#chat-form");
const input = document.querySelector("#message");
const messages = document.querySelector("#messages");
const statusEl = document.querySelector("#status");
const language = document.querySelector("#language");
const sendButton = form.querySelector(".send");
const mic = document.querySelector("#mic");
const speakButton = document.querySelector("#speak");
let history = [];
let busy = false;
let recognition = null;

function addMessage(text, who) {
  const el = document.createElement("article");
  el.className = "bubble " + who;
  el.textContent = text;
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
}
function speechLanguage(text) {
  if (language.value === "te" || /[\u0C00-\u0C7F]/.test(text)) return "te-IN";
  if (language.value === "hi" || /[\u0900-\u097F]/.test(text)) return "hi-IN";
  return "en-IN";
}
function speak(text) {
  if (!("speechSynthesis" in window)) {
    statusEl.textContent = "Speech playback is not supported in this browser.";
    return;
  }
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = speechLanguage(text);
  utterance.rate = 1;
  utterance.onstart = () => { statusEl.textContent = "Speaking…"; };
  utterance.onend = () => { statusEl.textContent = ""; };
  utterance.onerror = () => { statusEl.textContent = "Speech playback could not start."; };
  window.speechSynthesis.speak(utterance);
}
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message || busy) return;
  addMessage(message, "user");
  input.value = "";
  busy = true;
  sendButton.disabled = true;
  statusEl.textContent = "Thinking…";
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, language: language.value, history })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Request failed");
    addMessage(data.reply, "assistant");
    history.push({ role: "user", text: message }, { role: "model", text: data.reply });
    history = history.slice(-20);
    if (document.querySelector("#auto-speak").checked) speak(data.reply);
    else statusEl.textContent = "";
  } catch (error) {
    addMessage("Sorry, I couldn't connect just now. Please try again.", "assistant");
    statusEl.textContent = error.message;
  } finally {
    busy = false;
    sendButton.disabled = false;
    input.focus();
  }
});
document.querySelector("#new-chat").addEventListener("click", () => {
  if (recognition) recognition.stop();
  if ("speechSynthesis" in window) window.speechSynthesis.cancel();
  history = [];
  messages.replaceChildren();
  addMessage("Hello! నమస్కారం! नमस्ते! How can I help you today?", "assistant");
  statusEl.textContent = "";
});
speakButton.addEventListener("click", () => {
  if ("speechSynthesis" in window) window.speechSynthesis.cancel();
  statusEl.textContent = "Speech stopped.";
});
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (!SpeechRecognition) {
  mic.disabled = true;
  mic.title = "Speech recognition is not supported in this browser";
} else {
  mic.addEventListener("click", () => {
    if (recognition) recognition.stop();
    recognition = new SpeechRecognition();
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    recognition.lang = ({ auto: "en-IN", en: "en-IN", te: "te-IN", hi: "hi-IN" })[language.value];
    recognition.onstart = () => { statusEl.textContent = "Listening…"; mic.classList.add("listening"); };
    recognition.onerror = () => { statusEl.textContent = "Microphone unavailable. Check browser permission."; };
    recognition.onresult = (event) => {
      const result = event.results[event.results.length - 1];
      if (result.isFinal) {
        input.value = result[0].transcript;
        form.requestSubmit();
      }
    };
    recognition.onend = () => { mic.classList.remove("listening"); if (statusEl.textContent === "Listening…") statusEl.textContent = ""; };
    try { recognition.start(); } catch (_) { statusEl.textContent = "Microphone is already active."; }
  });
}
