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
    new_task = request.get_json()  # Get JSON data from the request body
    if not new_task or "title" not in new_task:
        return jsonify({"error": "Title is required"}), 400  # Return an error if no title

    new_task_id = max([task["id"] for task in tasks]) + 1 if tasks else 1  # Generate a new ID
    new_task_entry = {"id": new_task_id, "title": new_task["title"]}
    tasks.append(new_task_entry)  # Add the new task to the list
    return jsonify(new_task_entry), 201  # Return the newly created task

if __name__ == "__main__":
    app.run(debug=True)