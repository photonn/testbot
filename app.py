import os
import logging
from flask import Flask, request, jsonify
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes
from azure.monitor.opentelemetry import configure_azure_monitor

# Configure Application Insights using Azure Monitor OpenTelemetry (modern approach)
app_insights_connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
if app_insights_connection_string:
    # Configure Azure Monitor telemetry collection
    configure_azure_monitor(
        connection_string=app_insights_connection_string,
        logger_name=__name__
    )
    logging.info("Azure Monitor OpenTelemetry configured successfully")
else:
    # Fallback to basic logging if no connection string
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.warning("APPLICATIONINSIGHTS_CONNECTION_STRING not found, using basic logging")

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
logging.info("Starting Flask bot application.")

app_id = os.getenv("MICROSOFT_APP_ID")
app_password = os.getenv("MICROSOFT_APP_PASSWORD")
app_tenant_id = os.getenv("MICROSOFT_APP_TENANTID")  # Add tenant ID for cross-tenant scenarios
logging.info(f"Loaded environment variables: MICROSOFT_APP_ID={app_id}, MICROSOFT_APP_PASSWORD={'set' if app_password else 'unset'}, TENANT_ID={app_tenant_id}")
# Initialize the Bot Framework Adapter with environment variables for cross-tenant scenario
adapter_settings = BotFrameworkAdapterSettings(app_id, app_password)
if app_tenant_id:
    # Set tenant ID for cross-tenant scenarios
    adapter_settings.tenant_id = app_tenant_id
    logging.info(f"Cross-tenant configuration enabled with tenant ID: {app_tenant_id}")
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
