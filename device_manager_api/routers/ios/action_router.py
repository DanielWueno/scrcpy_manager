from flask import Blueprint, jsonify, request

action_router = Blueprint('action_router', __name__)

@action_router.route('/perform_action', methods=['POST'])
def perform_action():
    data = request.json
    action_type = data.get('action_type')
    
    # Here you would implement the logic for performing the action
    # For demonstration, we'll just return a success message
    return jsonify({
        "status": "success",
        "message": f"Action '{action_type}' performed successfully on iOS."
    }), 200

@action_router.route('/available_actions', methods=['GET'])
def available_actions():
    # This would typically fetch available actions from a database or service
    actions = ["action1", "action2", "action3"]
    return jsonify({
        "status": "success",
        "available_actions": actions
    }), 200