from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return jsonify({"message": "Webhook listener is running"}), 200

    # Check if Asana is verifying the webhook
    if "X-Hook-Secret" in request.headers:
        hook_secret = request.headers["X-Hook-Secret"]
        response = jsonify({"success": True})
        response.headers["X-Hook-Secret"] = hook_secret  # Required for Asana handshake
        return response, 200  # Must return 200 OK

    # Process incoming Asana webhook events
    data = request.json
    print("Received Webhook:", data)  # Debugging log
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(debug=True)
