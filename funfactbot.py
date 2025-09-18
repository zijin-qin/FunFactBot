import ollama
import re

conversation_history = []

# --- Keyword extraction ---
STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
    "you", "your", "yours", "yourself", "yourselves", 
    "he", "him", "his", "himself", "she", "her", "hers", "herself",
    "it", "its", "itself", "they", "them", "their", "theirs",
    "what", "which", "who", "whom", "this", "that", "these", "those",
    "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing",
    "a", "an", "the", "and", "but", "if", "or", "because", "as",
    "until", "while", "of", "at", "by", "for", "with", "about",
    "against", "between", "into", "through", "during", "before",
    "after", "above", "below", "to", "from", "up", "down", "in",
    "out", "on", "off", "over", "under", "again", "further",
    "then", "once", "here", "there", "when", "where", "why", "how",
    "all", "any", "both", "each", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same",
    "so", "than", "too", "very", "can", "will", "just", "don",
    "should", "now", "tell", "give", "fact", "facts", "about"
}

def extract_keywords(text, top_n=3):
    """Extract meaningful keywords from user input"""
    words = re.findall(r"\b[a-z']+\b", text.lower())
    keywords = [w for w in words if w not in STOPWORDS and len(w) > 2]
    return keywords[:top_n] if keywords else []

# --- Chatbot function ---
def get_response(user_input, bot_name, is_naming=False):
    global conversation_history

    keywords = extract_keywords(user_input)
    
    if keywords:
        keyword_str = ", ".join(keywords)
        topic_instruction = f"Focus on this topic/theme: {keyword_str}"
    else:
        topic_instruction = "Share any random interesting fun fact"

    # Special handling for when the bot is being named
    if is_naming:
        system_prompt = f"""
        You are a friendly fun fact bot that just got named "{user_input}"! 
        The user just gave you this name: "{user_input}"
        
        Your response should:
        1. Introduce yourself with your new name
        2. Share ONE interesting fun fact related to any part of your name
        
        IMPORTANT: Only share facts that are verifiably true and well-known. If you're not completely certain about a fact, don't make one up. Instead, say something like "Here's something interesting I believe about [topic], though you might want to verify this..."
        
        Guidelines:
        - For complex names like "Sir Pineapple the Narrator and Dino Beneath MIETTE 🍍👑", pick the most interesting element to make a fact about (like pineapples, dinosaurs, or narrators)
        - If it's a regular name, share a fact about that name, its meaning, or famous people with that name
        - Keep it conversational and engaging (2-4 sentences max)
        - Never use "..." in your responses
        - Make it genuinely interesting or surprising but TRUTHFUL
        - Stick to well-documented, commonly known facts
        
        Example format: "Hi there! I'm [your name]! Here's a fun fact about [element from name]: [verified fact]"
        """
    else:
        system_prompt = f"""
        You are {bot_name}, a friendly fun fact bot. 
        Your ONLY job is to share one quirky, interesting, or surprising fun fact per response.
        {topic_instruction}
        
        CRITICAL ACCURACY RULES:
        - ONLY share facts that are verifiably true and well-documented
        - NEVER make up names, places, statistics, or scientific claims
        - If you're unsure about something, say "Here's something interesting I believe about [topic], though you should double-check this..." 
        - Stick to commonly known, well-established facts
        - When in doubt, choose a different angle or a more general fact you're confident about
        
        OTHER IMPORTANT RULES:
        - You MUST share exactly ONE fun fact in every single response
        - NEVER ask questions back to the user
        - NEVER say things like "What would you like to know?" or "Tell me more"
        - Focus ONLY on giving interesting facts
        - Keep it conversational but always end with a fact, not a question
        - Never use "..." in your responses
        - Keep responses concise but engaging (2-4 sentences max)
        
        Format: Start with something like "Here's a fun fact about [topic]:" or "Did you know that..." then give the VERIFIED fact.
        """

    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history (skip for naming since it's the first interaction)
    if not is_naming:
        # Only include the last few exchanges to prevent the bot from getting confused
        recent_history = conversation_history[-8:] if len(conversation_history) > 8 else conversation_history
        for i in range(0, len(recent_history), 2):
            if i+1 < len(recent_history):  # Make sure we have both user and assistant messages
                user_msg = recent_history[i].replace("User: ", "")
                bot_msg = recent_history[i+1].replace(f"{bot_name}: ", "")
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": bot_msg})

    messages.append({"role": "user", "content": user_input})

    try:
        response = ollama.chat(model="gemma3:1b", messages=messages)
        # Handle different possible response formats from Ollama
        if hasattr(response, 'message') and hasattr(response.message, 'content'):
            reply = response.message.content
        elif isinstance(response, dict) and "message" in response and "content" in response["message"]:
            reply = response["message"]["content"]
        elif isinstance(response, dict) and "content" in response:
            reply = response["content"]
        else:
            reply = "I got a response but couldn't parse it properly. Let me try again!"
    except Exception as e:
        reply = f"Oops! I'm having trouble connecting to get you a fun fact right now. Error: {e}"

    # Store in conversation history
    conversation_history.append(f"User: {user_input}")
    conversation_history.append(f"{bot_name}: {reply}")

    # Keep history manageable (last 10 exchanges)
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]

    return reply