from flask import Flask, request, jsonify
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
import os


app = Flask(__name__)

# Configure Azure Application Insights
connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")
logger = logging.getLogger(__name__)
if connection_string:
    logger.addHandler(AzureLogHandler(connection_string=connection_string))
    logger.setLevel(logging.INFO)


# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/messages', methods=['POST'])
def echo():
    data = request.json
    user_message = data.get('text', '')
    reply = {"type": "message", "text": f"You said: {user_message}"}
    # Log the incoming message to Application Insights
    logger.info(f"Received message: {user_message}")
    return jsonify(reply)

if __name__ == '__main__':
    app.run(debug=True, port=3978)
