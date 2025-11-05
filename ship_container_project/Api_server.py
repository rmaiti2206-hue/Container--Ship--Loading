from flask import Flask, request, jsonify
import database as db

app = Flask(__name__)
db.setup_database()

@app.route('/api/containers', methods=['GET'])
def list_containers():
    containers = db.get_all_containers()
    return jsonify(containers)

@app.route('/api/container', methods=['POST'])
def add_container():
    data = request.json
    db.add_container(data['name'], data['weight'], data['destination'], data['type'])
    return jsonify({"message": "Container added successfully"}), 201

@app.route('/api/status', methods=['GET'])
def status():
    total = db.get_total_weight()
    capacity = db.get_ship_capacity()
    remaining = capacity - total
    return jsonify({
        "capacity": capacity,
        "used": total,
        "remaining": remaining
    })
@app.route('/api/containers', methods=['DELETE'])
def delete_all():
    db.delete_all_containers()
    return jsonify({"message": "All containers deleted successfully!"}), 200


if __name__ == '__main__':
    app.run(debug=True)
