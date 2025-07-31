import os
import logging
from flask import Flask, request, jsonify
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Initialize the Bot Framework Adapter
adapter_settings = BotFrameworkAdapterSettings("YourAppID", "YourAppPassword")
adapter = BotFrameworkAdapter(adapter_settings)

app_id = os.getenv("MICROSOFT_APP_ID")
app_password = os.getenv("MICROSOFT_APP_PASSWORD")

# Define the bot's behavior
class EchoBot:
    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == ActivityTypes.message:
            logging.info(f"Received message: {turn_context.activity.text}")
            await turn_context.send_activity(f"You said: {turn_context.activity.text}")
            logging.info(f"Sent echo response: 'You said: {turn_context.activity.text}'")

# Instantiate the bot
bot = EchoBot()

# Define the /api/messages endpoint
@app.route("/api/messages", methods=["POST"])
async def messages():
    if "application/json" in request.headers["Content-Type"]:
        activity = Activity().deserialize(request.json)
        auth_header = request.headers.get("Authorization", "")
        logging.info(f"Processing activity: {activity}")
        response = await adapter.process_activity(activity, auth_header, bot.on_turn)
        if response:
            logging.info(f"Response: {response.body}")
            return jsonify(response.body), response.status
        return "", 202
    else:
        logging.warning("Invalid content type")
        return "Content-Type must be application/json", 415

# Define the /health endpoint
@app.route("/health", methods=["GET"])
def health_check():
    logging.info("Health check requested")
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=3978)
