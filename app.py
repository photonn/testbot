from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/messages', methods=['POST'])
def echo():
    data = request.json
    user_message = data.get('text', '')
    reply = {"type": "message", "text": f"You said: {user_message}"}
    return jsonify(reply)

if __name__ == '__main__':
    app.run(debug=True, port=3978)
