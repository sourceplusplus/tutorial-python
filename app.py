import os
import threading
import time
from datetime import datetime

from flask import Flask, send_from_directory, request, jsonify

app = Flask(__name__)

todos = {}

FIVE_MINUTES_MILLIS = 5 * 60 * 1000


@app.before_first_request
def setup():
    def cleanup():
        for key, value in list(todos.items()):
            if value.get("completed", False) is True:
                delete_date = datetime.fromtimestamp(time.time() - FIVE_MINUTES_MILLIS * 1000)
                if datetime.fromtimestamp(value.get("createDate")) < delete_date:
                    del todos[key]
        threading.Timer(1, cleanup).start()

    cleanup()


@app.route('/todos/clear_completed', methods=['DELETE'])
def clear_completed():
    for key, value in list(todos.items()):
        if value.get("completed", False) is True and value.get("id") is None:
            print("Deleting: " + key)
            del todos[key]
        else:
            print("Not deleting: " + key)
    return "OK"


@app.route('/')
def root():
    return send_from_directory("static", "index.html")


@app.route("/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)


@app.route('/todos', methods=['GET'])
def get_todos():
    if len(todos) == 0:
        return jsonify([])
    return jsonify(list(todos.values()))


@app.route('/todos/<id>', methods=['GET'])
def get_todo(id):
    return todos.get(id, 'Not Found')


@app.route('/todos/dup/<id>', methods=['POST'])
def duplicate_todo(id):
    dupe_todo = todos.get(id, 'Not Found').copy()
    dupe_todo["id"] = os.urandom(16).hex()
    todos[dupe_todo["id"]] = dupe_todo
    return dupe_todo


@app.route('/todos', methods=['POST'])
def add_todo():
    todo = request.get_json()
    if len(todo.get("title")) == 0:
        return "Bad Request"

    todo["id"] = os.urandom(16).hex()
    todo["createDate"] = round(time.time())
    todos[todo["id"]] = todo
    return todo


@app.route('/todos/<id>', methods=['DELETE'])
def delete_todo(id):
    if id in todos:
        del todos[id]
        return "OK"
    return "Not Found"


@app.route('/todos', methods=['DELETE'])
def delete_all_todos():
    todos.clear()
    return "OK"


@app.route('/todos/clear-completed', methods=['DELETE'])
def clear_completed_todos():
    for key, value in todos.items():
        if value.get("completed", False) is True:
            del todos[key]
    return "OK"


@app.route('/todos', methods=['PUT'])
def update_todo():
    todo = request.get_json()
    if todo["id"] in todos:
        todos[todo["id"]] = todo
        return todo
    return "Not Found"


if __name__ == '__main__':
    from sourceplusplus.SourcePlusPlus import SourcePlusPlus
    SourcePlusPlus({
        "spp.platform_host": "spp-platform",
        "skywalking.collector.backend_service": "skywalking-oap:11800",
        "spp.disable_tls": True
    }).attach()

    app.run(host='0.0.0.0', port=8080)
