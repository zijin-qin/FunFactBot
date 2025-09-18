from flask import Flask, render_template, request, jsonify
import funfactbot  # your funfactbot.py

app = Flask(__name__)
bot_name = None
bot_initialized = False  # Track if bot has been named

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    global bot_name, bot_initialized
    user_input = request.json.get("message", "")

    # If bot_name is not set, treat the first message as the bot's name
    if bot_name is None:
        bot_name = user_input.strip() or "FunFactBot"
        bot_initialized = True
        # Treat the name as the first topic and generate a fun fact about it
        reply = funfactbot.get_response(user_input, bot_name, is_naming=True)
        return jsonify({"reply": reply})

    # Now pass user input to get_response for normal conversation
    reply = funfactbot.get_response(user_input, bot_name)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)