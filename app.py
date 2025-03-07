from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return jsonify({"message": "Webhook listener is running"}), 200

    # Log the request for debugging
    print("✅ Received Webhook Headers:", request.headers)
    print("✅ Received Webhook Body:", request.json)

    # Handle Asana handshake verification
    if "X-Hook-Secret" in request.headers:
        hook_secret = request.headers["X-Hook-Secret"]
        response = jsonify({"success": True})
        response.headers["X-Hook-Secret"] = hook_secret
        return response, 200

    # Process incoming Asana webhook events
    data = request.json
    if "events" in data:
        print("📌 Webhook Event Data:", data["events"])  # Print actual event data
    
    return jsonify({"status": "received", "data": data}), 200

if __name__ == "__main__":
    app.run(debug=True)
