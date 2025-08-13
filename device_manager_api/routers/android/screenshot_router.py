from flask import Blueprint, request, jsonify
from api.utils import ensure_directory_exists
import logging

screenshot_router = Blueprint('screenshot_router', __name__)

logger = logging.getLogger(__name__)

@screenshot_router.route('/screenshot', methods=['POST'])
def take_screenshot():
    data = request.json
    device_id = data.get('device_id')
    
    if not device_id:
        logger.error("Device ID is required")
        return jsonify({"error": "Device ID is required"}), 400
    
    # Logic to take a screenshot for the specified device
    # This is a placeholder for the actual screenshot logic
    logger.info(f"Taking screenshot for device: {device_id}")
    
    # Simulate screenshot taking
    screenshot_path = f"/path/to/screenshots/{device_id}.png"
    ensure_directory_exists("/path/to/screenshots")
    
    # Return the path of the screenshot taken
    return jsonify({"screenshot_path": screenshot_path}), 200

@screenshot_router.route('/screenshot/<device_id>', methods=['GET'])
def get_screenshot(device_id):
    # Logic to retrieve the screenshot for the specified device
    logger.info(f"Retrieving screenshot for device: {device_id}")
    
    # Simulate retrieval of screenshot
    screenshot_path = f"/path/to/screenshots/{device_id}.png"
    
    # Check if the screenshot exists
    # This is a placeholder for actual existence check
    if False:  # Replace with actual check
        return jsonify({"error": "Screenshot not found"}), 404
    
    return jsonify({"screenshot_path": screenshot_path}), 200