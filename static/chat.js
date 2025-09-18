let botNamed = false;
let botName = "";

async function sendMessage() {
    const input = document.getElementById("userInput");
    const message = input.value.trim();
    const messagesDiv = document.getElementById("messages");
    const button = document.querySelector("button");
    const chatbox = document.querySelector(".chatbox");
    
    if (!message) return;

    if (!botNamed) {
        // First message is the bot's name
        botName = message || "FunFactBot";
        botNamed = true;

        // Expand the chatbox for conversation
        chatbox.classList.add("expanded");

        // Clear the naming prompt
        messagesDiv.innerHTML = "";

        // Update the title (truncate if too long for display)
        const displayName = botName.length > 25 ? botName.substring(0, 25) + "..." : botName;
        document.getElementById("title").innerText = displayName;
        
        // Update input placeholder and button text for normal conversation
        input.placeholder = "Give me a topic for a fun fact...";
        button.innerText = "Send";

        // Clear the input field immediately
        input.value = "";

        // Show loading indicator for the introduction
        const loadingId = 'loading-intro';
        messagesDiv.innerHTML += `<div class="message loading chat-message" id="${loadingId}"><b>${displayName}:</b> Thinking of a fun fact about my name</div>`;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;

        // Get the bot's introduction and fun fact about its name
        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: message })
            });
            const data = await response.json();
            
            // Remove loading and show introduction
            document.getElementById(loadingId).remove();
            messagesDiv.innerHTML += `<div class="bot chat-message"><b>${displayName}:</b> ${data.reply}</div>`;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
        } catch (error) {
            document.getElementById(loadingId).remove();
            messagesDiv.innerHTML += `<div class="bot chat-message"><b>${displayName}:</b> Sorry, I'm having trouble connecting right now!</div>`;
        }
        return;
    }

    // Normal user message - show it first
    messagesDiv.innerHTML += `<div class="user chat-message"><b>You:</b> ${message}</div>`;
    input.value = "";
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    // Show loading indicator
    const displayName = botName.length > 25 ? botName.substring(0, 25) + "..." : botName;
    const loadingId = 'loading-' + Date.now();
    messagesDiv.innerHTML += `<div class="message loading chat-message" id="${loadingId}"><b>${displayName}:</b> Thinking of a fun fact</div>`;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    try {
        // Get bot response
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        
        // Remove loading and show response
        document.getElementById(loadingId).remove();
        messagesDiv.innerHTML += `<div class="bot chat-message"><b>${displayName}:</b> ${data.reply}</div>`;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        
    } catch (error) {
        document.getElementById(loadingId).remove();
        messagesDiv.innerHTML += `<div class="bot chat-message"><b>${displayName}:</b> Sorry, I'm having trouble right now!</div>`;
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById("userInput");
    const messagesDiv = document.getElementById("messages");
    
    // Add naming prompt initially
    messagesDiv.innerHTML = `<div class="naming-prompt">Give me a name!</div>`;
    
    // Enter key support
    input.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });
    
    // Focus on input initially
    input.focus();
});