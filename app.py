import os
import logging
from flask import Flask, request, jsonify
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler

# Configure Application Insights logging
app_insights_connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
if app_insights_connection_string:
    # Configure logging to send to Application Insights
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.addHandler(AzureLogHandler(connection_string=app_insights_connection_string))
    logger.setLevel(logging.INFO)
    logging.info("Application Insights logging configured successfully")
else:
    # Fallback to basic logging if no connection string
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.warning("APPLICATIONINSIGHTS_CONNECTION_STRING not found, using basic logging")

app = Flask(__name__)
logging.info("Starting Flask bot application.")

# Configure Application Insights tracing for Flask
if app_insights_connection_string:
    middleware = FlaskMiddleware(
        app,
        exporter=AzureExporter(connection_string=app_insights_connection_string),
        sampler=ProbabilitySampler(rate=1.0)
    )
    logging.info("Application Insights tracing middleware configured for Flask")

app_id = os.getenv("MICROSOFT_APP_ID")
app_password = os.getenv("MICROSOFT_APP_PASSWORD")
logging.info(f"Loaded environment variables: MICROSOFT_APP_ID={app_id}, MICROSOFT_APP_PASSWORD={'set' if app_password else 'unset'}")
# Initialize the Bot Framework Adapter with environment variables
adapter_settings = BotFrameworkAdapterSettings(app_id, app_password)
adapter = BotFrameworkAdapter(adapter_settings)
logging.info("BotFrameworkAdapter initialized.")

# Define the bot's behavior
class EchoBot:
    async def on_turn(self, turn_context: TurnContext):
        logging.info(f"Bot on_turn called. Activity type: {turn_context.activity.type}")
        if turn_context.activity.type == ActivityTypes.message:
            logging.info(f"Received user message: {turn_context.activity.text}")
            await turn_context.send_activity(f"You said: {turn_context.activity.text}")
            logging.info(f"Echoed back: You said: {turn_context.activity.text}")
        else:
            logging.info(f"Received non-message activity: {turn_context.activity.type}")

logging.info("Instantiating EchoBot.")
bot = EchoBot()

import asyncio
# Define the /api/messages endpoint (sync for Flask)
@app.route("/api/messages", methods=["POST"])
def messages():
    logging.info("/api/messages endpoint called.")
    try:
        content_type = request.headers.get("Content-Type", "")
        logging.info(f"Request Content-Type: {content_type}")
        if "application/json" in content_type:
            logging.info(f"Request JSON: {request.json}")
            activity = Activity().deserialize(request.json)
            logging.info(f"Deserialized activity: {activity}")
            auth_header = request.headers.get("Authorization", "")
            logging.info(f"Authorization header: {auth_header}")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logging.info("Processing activity with bot adapter.")
            response = loop.run_until_complete(
                adapter.process_activity(activity, auth_header, bot.on_turn)
            )
            if response:
                logging.info(f"Adapter response: {response.body}, status: {response.status}")
                return jsonify(response.body), response.status
            logging.info("No response from bot adapter, returning 202.")
            return "", 202
        else:
            logging.warning("Invalid content type")
            return "Content-Type must be application/json", 415
    except Exception as e:
        print(f"Exception in /api/messages: {e}", flush=True)
        logging.error(f"Exception in /api/messages: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Define the /health endpoint
@app.route("/health", methods=["GET"])
def health_check():
    logging.info("/health endpoint called.")
    logging.info("Health check requested")
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    logging.info("Running Flask app in debug mode on port 3978.")
    app.run(debug=True, port=3978)
