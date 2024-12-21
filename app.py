from flask import Flask, jsonify, request
import json  # Module for handling JSON file operations

app = Flask(__name__)

# Define the file for storing tasks and functions for saving/loading tasks
TASKS_FILE = "tasks.json"

# Define a reusable function to format error responses
def error_response(message, status):
    # Create a JSON response containing the error message
    response = jsonify({"error": message})
    # Attach the HTTP status code to the response
    response.status_code = status
    # Return the formatted response
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
    # Check if the server is running
    return "Task Manager API is running!"

@app.route("/tasks", methods=["GET"])
def get_tasks():
    # Return filtered tasks based on query parameters or all tasks if none provided
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
    
    return jsonify(filtered_tasks)

@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task_by_id(task_id):
    # Retrieve a task by its ID or return an error if not found
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        return error_response("Task not found", 404)
    return jsonify(task)

@app.route("/tasks", methods=["POST"])
def add_task():
    # Add a new task to the list and save it to the JSON file
    new_task = request.get_json()
    if not new_task or "title" not in new_task:
        return error_response("Title is required", 400)
    
    new_task_id = max([task["id"] for task in tasks]) + 1 if tasks else 1
    new_task_entry = {
        "id": new_task_id,
        "title": new_task["title"],
        "completed": False  # Default completed status
    }
    
    tasks.append(new_task_entry)
    save_tasks_to_file()
    return jsonify(new_task_entry), 201

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    # Update a task's title or completion status by ID and save changes to the JSON file
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        return error_response("Task not found", 404)

    updated_data = request.get_json()
    if "title" in updated_data:
        task["title"] = updated_data["title"]
    if "completed" in updated_data:
        task["completed"] = updated_data["completed"]
    
    save_tasks_to_file()
    return jsonify(task), 200

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    # Search for the task by ID
    task = next((task for task in tasks if task["id"] == task_id), None)

    # Return an error response if the task is not found
    if not task:
        return error_response("Task not found", 404)

    # Remove the task if found
    tasks = [task for task in tasks if task["id"] != task_id]

    # Save updated tasks to the file
    save_tasks_to_file()

    # Return success message with 200 status code
    return jsonify({"message": "Task deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)