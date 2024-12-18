from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory task list (database)
tasks = [
    {"id": 1, "title": "Learn Flask"},
    {"id": 2, "title": "Build a Task Manager API"}
]

# GET route to return all tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks), 200

# POST route to create a new task
@app.route("/tasks", methods=["POST"])
def add_task():
    new_task = request.get_json()  # Get the data from the request body
    if not new_task or "title" not in new_task:
        return jsonify({"error": "Title is required"}), 400  # If no title, return error
    
    # Generate a unique ID for the new task
    new_task_id = max([task["id"] for task in tasks]) + 1 if tasks else 1
    new_task_entry = {"id": new_task_id, "title": new_task["title"]}
    
    tasks.append(new_task_entry)  # Add the task to the in-memory list
    return jsonify(new_task_entry), 201  # Return the created task with a 201 status code


# PUT route to update an existing task
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = next((task for task in tasks if task["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404  # Task not found
    
    updated_data = request.get_json()  # Get updated data from the request body
    if "title" in updated_data:
        task["title"] = updated_data["title"]  # Update the title if it's provided
    else:
        return jsonify({"error": "Title is required for update"}), 400  # Return error if no title
    
    return jsonify(task), 200  # Return the updated task with a 200 status code

# DELETE route to delete a task
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = next((task for task in tasks if task["id"] == task_id), None)  # Find the task by ID
    if not task:
        return jsonify({"error": "Task not found"}), 404  # Return error if task not found

    tasks.remove(task)  # Remove the task from the list
    return '', 204  # Return a 204 status (No Content) to indicate successful deletion

if __name__ == "__main__":
    app.run(debug=True)