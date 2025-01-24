import secrets
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

app = Flask(__name__)

# Generate a random 256-bit key (32 bytes) and set it as the JWT secret key
app.config["JWT_SECRET_KEY"] = secrets.token_hex(32)  # Secure and random key generation

jwt = JWTManager(app)

# Your other routes and logic here...

# Define the file for storing tasks and functions for saving/loading tasks
TASKS_FILE = "tasks.json"

# Define a reusable function to format error responses
def error_response(message, status):
    response = jsonify({"error": message})
    response.status_code = status
    return response

# Load tasks from the JSON file or return an empty list if the file doesn't exist
def load_tasks_from_file():
    try:
        with open(TASKS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save the current list of tasks to the JSON file
def save_tasks_to_file():
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)

# Load tasks from the JSON file when the app starts
tasks = load_tasks_from_file()

@app.route("/")
def home():
    return "Task Manager API is running!"

@app.route("/tasks", methods=["GET"])
@jwt_required()  # Protect this route with JWT authentication
def get_tasks():
    filtered_tasks = tasks
    title = request.args.get("title")
    completed = request.args.get("completed")

    if title:
        filtered_tasks = [task for task in filtered_tasks if title.lower() in task["title"].lower()]
    
    if completed:
        if completed.lower() not in ["true", "false"]:
            return error_response("Invalid value for 'completed'. Use 'true' or 'false'.", 400)
        is_completed = completed.lower() == "true"
        filtered_tasks = [task for task in filtered_tasks if task.get("completed") == is_completed]

    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=len(filtered_tasks), type=int)

    if page < 1 or limit < 1:
        return error_response("Page and limit must be positive integers.", 400)

    start = (page - 1) * limit
    end = start + limit
    filtered_tasks = filtered_tasks[start:end]

    return jsonify(filtered_tasks), 200

@app.route("/tasks/<int:task_id>", methods=["GET"])
@jwt_required()  # Protect this route with JWT authentication
def get_task_by_id(task_id):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        return error_response("Task not found", 404)
    return jsonify(task)

@app.route("/tasks", methods=["POST"])
@jwt_required()  # Protect this route with JWT authentication
def add_task():
    new_task = request.get_json()

    if not new_task or "title" not in new_task:
        return error_response("Title is required.", 400)
    if not isinstance(new_task["title"], str) or not new_task["title"].strip():
        return error_response("Title must be a non-empty string.", 400)
    if len(new_task["title"]) > 100:
        return error_response("Title must be 100 characters or fewer.", 400)
    if re.search(r"[<>/]", new_task["title"]):
        return error_response("Title contains prohibited characters.", 400)

    new_task_id = max([task["id"] for task in tasks]) + 1 if tasks else 1
    new_task_entry = {
        "id": new_task_id,
        "title": new_task["title"],
        "completed": False
    }

    tasks.append(new_task_entry)
    save_tasks_to_file()

    return jsonify(new_task_entry), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()  # Protect this route with JWT authentication
def update_task(task_id):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        return error_response("Task not found", 404)

    try:
        updates = request.get_json()
    except Exception:
        return error_response("Invalid JSON payload", 400)

    if not updates:
        return error_response("Request payload is required", 400)

    allowed_fields = {"title", "completed"}
    unexpected_fields = set(updates.keys()) - allowed_fields
    if unexpected_fields:
        return error_response(f"Unexpected fields: {', '.join(unexpected_fields)}", 400)

    if "title" in updates:
        if not isinstance(updates["title"], str) or not updates["title"].strip():
            return error_response("Title must be a non-empty string", 400)

    if "completed" in updates:
        if not isinstance(updates["completed"], bool):
            return error_response("Completed field must be true or false", 400)

    task.update({key: value for key, value in updates.items() if key in allowed_fields})
    save_tasks_to_file()

    return jsonify(task), 200

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()  # Protect this route with JWT authentication
def delete_task(task_id):
    global tasks

    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        return error_response("Task not found", 404)

    tasks = [task for task in tasks if task["id"] != task_id]
    save_tasks_to_file()

    return jsonify({"message": "Task deleted"}), 200

@app.route("/tasks/<int:task_id>", methods=["PATCH"])
@jwt_required()  # Protect this route with JWT authentication
def update_task_status(task_id):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        return error_response("Task not found", 404)

    updated_data = request.get_json()
    if not updated_data or "completed" not in updated_data:
        return error_response("Field 'completed' is required and must be a boolean", 400)
    
    if not isinstance(updated_data["completed"], bool):
        return error_response("Field 'completed' must be true or false", 400)

    task["completed"] = updated_data["completed"]
    save_tasks_to_file()

    return jsonify(task), 200

# Authentication routes
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        return error_response("Username and password are required", 400)

    username = data["username"]
    password = data["password"]

    # For simplicity, assume a fixed username and password
    if username == "admin" and password == "password":
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return error_response("Invalid credentials", 401)

if __name__ == "__main__":
    app.run(debug=True)