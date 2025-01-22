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

    # Filter tasks by title if provided
    if title:
        filtered_tasks = [task for task in filtered_tasks if title.lower() in task["title"].lower()]
    
    # Filter tasks by completion status if provided
    if completed:
        if completed.lower() not in ["true", "false"]:
            # Return an error if "completed" is not "true" or "false"
            return error_response("Invalid value for 'completed'. Use 'true' or 'false'.", 400)
        is_completed = completed.lower() == "true"
        filtered_tasks = [task for task in filtered_tasks if task.get("completed") == is_completed]
    
    # Pagination logic
    page = request.args.get("page", default=1, type=int)  # Get the 'page' query parameter or default to 1
    limit = request.args.get("limit", default=len(filtered_tasks), type=int)  # Get 'limit' or default to all tasks

    # Validate 'page' and 'limit' as positive integers
    if page < 1 or limit < 1:
        # Return an error response if 'page' or 'limit' is invalid
        return error_response("Page and limit must be positive integers.", 400)

    # Calculate the start and end indices for slicing the tasks list
    start = (page - 1) * limit
    end = start + limit

    # Slice the filtered tasks for pagination
    filtered_tasks = filtered_tasks[start:end]

    # Return the filtered and paginated tasks with a 200 status
    return jsonify(filtered_tasks), 200

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
    try:
        new_task = request.get_json()  # Parse JSON request body
    except Exception:
        return error_response("Invalid JSON format", 400)  # Error if body is not JSON
    
    # Check if 'title' exists and is a non-empty string
    if not new_task or "title" not in new_task:
        return error_response("Title is required", 400)
    if not isinstance(new_task["title"], str) or not new_task["title"].strip():
        return error_response("Title must be a non-empty string", 400)
    
    # Assign a new ID and add the task to the list
    new_task_id = max([task["id"] for task in tasks]) + 1 if tasks else 1
    new_task_entry = {
        "id": new_task_id,
        "title": new_task["title"].strip(),  # Strip extra spaces
        "completed": False  # Default completed status
    }
    
    tasks.append(new_task_entry)
    save_tasks_to_file()  # Save to file
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
    global tasks  # This tells Python that we're referring to the global 'tasks' variable

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

@app.route("/tasks/<int:task_id>", methods=["PATCH"])
def update_task_status(task_id):
    # Find the task by its ID
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        # Return an error response if the task is not found
        return error_response("Task not found", 404)

    # Get the request payload and validate it
    updated_data = request.get_json()
    if not updated_data or "completed" not in updated_data:
        # Return an error response if the "completed" field is missing or invalid
        return error_response("Field 'completed' is required and must be a boolean", 400)
    
    # Ensure the value for "completed" is a boolean
    if not isinstance(updated_data["completed"], bool):
        # Return an error response if "completed" is not a boolean
        return error_response("Field 'completed' must be true or false", 400)

    # Update the "completed" status of the task
    task["completed"] = updated_data["completed"]

    # Save the updated tasks to the JSON file
    save_tasks_to_file()

    # Return the updated task as a response
    return jsonify(task), 200

if __name__ == "__main__":
    app.run(debug=True)