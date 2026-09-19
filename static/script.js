/**
 * script.js
 * ---------
 * Handles all frontend interactivity for the chat interface:
 *   - Sending the user's message to the Flask backend (POST /chat)
 *   - Rendering both user and bot messages as chat bubbles
 *   - Showing a "typing..." indicator while waiting for a response
 *   - Basic client-side validation (no empty messages)
 *   - Resetting the conversation context via POST /reset
 */

const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const chatWindow = document.getElementById("chat-window");
const typingIndicator = document.getElementById("typing-indicator");
const errorMessageEl = document.getElementById("error-message");
const resetBtn = document.getElementById("reset-btn");

/**
 * Append a new chat bubble to the chat window.
 * @param {string} text - The message text to display.
 * @param {"user"|"bot"} sender - Who sent the message.
 */
function appendMessage(text, sender) {
  const messageEl = document.createElement("div");
  messageEl.classList.add("message", sender === "user" ? "user-message" : "bot-message");

  const bubble = document.createElement("div");
  bubble.classList.add("bubble");
  bubble.textContent = text;

  messageEl.appendChild(bubble);
  chatWindow.appendChild(messageEl);

  // Auto-scroll to the latest message
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function showError(message) {
  errorMessageEl.textContent = message;
  errorMessageEl.classList.remove("hidden");
  setTimeout(() => errorMessageEl.classList.add("hidden"), 4000);
}

function setTyping(isTyping) {
  typingIndicator.classList.toggle("hidden", !isTyping);
  if (isTyping) {
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }
}

/**
 * Send the user's message to the backend and display the bot's reply.
 */
async function sendMessage(message) {
  setTyping(true);

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();

    setTyping(false);

    if (!response.ok) {
      // Server returned a 4xx/5xx with an { error: "..." } payload
      showError(data.error || "Something went wrong. Please try again.");
      return;
    }

    appendMessage(data.response, "bot");
  } catch (err) {
    setTyping(false);
    showError("Could not reach the server. Please check your connection.");
    console.error(err);
  }
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const message = userInput.value.trim();

  // Client-side validation: never send an empty message
  if (!message) {
    showError("Please type a message before sending.");
    return;
  }

  appendMessage(message, "user");
  userInput.value = "";
  sendMessage(message);
});

resetBtn.addEventListener("click", async () => {
  try {
    await fetch("/reset", { method: "POST" });
  } catch (err) {
    console.error("Failed to reset context:", err);
  }

  chatWindow.innerHTML = "";
  appendMessage(
    "Conversation reset. Hi again! 👋 Ask me about your account, services, payments, refunds, or contact info.",
    "bot"
  );
  userInput.focus();
});

// Focus the input field as soon as the page loads
window.addEventListener("load", () => userInput.focus());
