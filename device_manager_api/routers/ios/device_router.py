from flask import Blueprint, jsonify, request

device_router = Blueprint('ios_device_router', __name__)

@device_router.route('/devices', methods=['GET'])
def get_devices():
    return jsonify({"message": "List of iOS devices"}), 200

@device_router.route('/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    return jsonify({"message": f"Details of iOS device {device_id}"}), 200

@device_router.route('/devices', methods=['POST'])
def add_device():
    device_data = request.json
    return jsonify({"message": "iOS device added", "device": device_data}), 201

@device_router.route('/devices/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    return jsonify({"message": f"iOS device {device_id} deleted"}), 204