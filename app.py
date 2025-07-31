
import logging
from flask import Flask, request, jsonify



app = Flask(__name__)

# Configure standard logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/messages', methods=['POST'])
def echo():
    try:
        data = request.json
        user_message = data.get('text', '')
        reply = {"type": "message", "text": f"You said: {user_message}"}
        # Log the incoming message
        logger.info(f"Received message: {user_message}")
        return jsonify(reply)
    except Exception as e:
        logger.error(f"Error in /api/messages: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3978)
