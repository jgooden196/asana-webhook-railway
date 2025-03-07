import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Load Asana API credentials
ASANA_TOKEN = os.getenv("ASANA_TOKEN")
ASANA_PROJECT_ID = os.getenv("ASANA_PROJECT_ID")

HEADERS = {
    "Authorization": f"Bearer {ASANA_TOKEN}"
}

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return jsonify({"message": "Webhook listener is running"}), 200

    print("✅ Received Webhook Headers:", request.headers)
    print("✅ Received Webhook Body:", request.json)

    # Handle Asana handshake verification
    if "X-Hook-Secret" in request.headers:
        response = jsonify({"success": True})
        response.headers["X-Hook-Secret"] = request.headers["X-Hook-Secret"]
        return response, 200

    # Process incoming Asana webhook events
    data = request.json
    if "events" in data:
        print("📌 Webhook Event Data:", data["events"])
        update_project_status()

    return jsonify({"status": "received", "data": data}), 200


def get_project_tasks():
    """Fetch all tasks in the Asana project."""
    url = f"https://app.asana.com/api/1.0/projects/{ASANA_PROJECT_ID}/tasks"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"⚠️ Error fetching tasks: {response.text}")
        return []


def get_task_details(task_id):
    """Fetch task details including custom fields for Budget and Actual Cost."""
    url = f"https://app.asana.com/api/1.0/tasks/{task_id}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json().get("data", {})
    else:
        print(f"⚠️ Error fetching task {task_id}: {response.text}")
        return {}


def update_project_status():
    """Calculate project metrics and update the Project Status task."""
    tasks = get_project_tasks()
    total_budget = 0
    total_actual_cost = 0
    over_budget_tasks = 0
    status_task_id = None

    for task in tasks:
        task_details = get_task_details(task["gid"])
        custom_fields = task_details.get("custom_fields", [])

        budget = actual_cost = 0
        for field in custom_fields:
            if field.get("name") == "Budget":
                budget = field.get("number_value", 0)
            elif field.get("name") == "Actual Cost":
                actual_cost = field.get("number_value", 0)

        total_budget += budget
        total_actual_cost += actual_cost

        if actual_cost > budget:
            over_budget_tasks += 1

        if task_details.get("name") == "Project Status":
            status_task_id = task["gid"]

    # Update the Project Status task
    if status_task_id:
        update_task_description(status_task_id, total_budget, total_actual_cost, over_budget_tasks)
    else:
        print("⚠️ Project Status task not found!")


def update_task_description(task_id, total_budget, total_actual_cost, over_budget_tasks):
    """Update the Project Status task with calculated metrics."""
    url = f"https://app.asana.com/api/1.0/tasks/{task_id}"
    description = (
        f"📊 **Project Summary**\n"
        f"- **Total Estimated Budget:** ${total_budget:,.2f}\n"
        f"- **Total Actual Cost:** ${total_actual_cost:,.2f}\n"
        f"- **Over-Budget Tasks:** {over_budget_tasks}\n"
    )

    data = {"notes": description}
    response = requests.put(url, headers=HEADERS, json=data)

    if response.status_code == 200:
        print("✅ Project Status updated successfully!")
    else:
        print(f"⚠️ Error updating task: {response.text}")


if __name__ == "__main__":
    app.run(debug=True)
