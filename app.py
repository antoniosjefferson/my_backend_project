from flask import Flask, jsonify

app = Flask(__name__)

# Sample in-memory tasks list (acting like a database)
tasks = [
    {"id": 1, "title": "Learn Flask"},
    {"id": 2, "title": "Build a Task Manager API"}
]

# GET route to return all tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks), 200  # Convert the tasks list to JSON and return it

if __name__ == "__main__":
    app.run(debug=True)