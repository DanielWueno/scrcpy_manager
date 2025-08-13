from flask import Blueprint, request, jsonify, send_file, current_app
from api.utils import ensure_directory_exists
import logging
import os
import platform

screenshot_router = Blueprint('screenshot_router', __name__)

logger = logging.getLogger(__name__)

def get_screenshot_dir():
    # Carpeta Pictures del usuario
    if platform.system() == "Windows":
        pictures_dir = os.path.join(os.environ["USERPROFILE"], "Pictures")
    else:
        pictures_dir = os.path.expanduser("~/Pictures")
    return pictures_dir

@screenshot_router.route('/screenshot', methods=['POST'])
def take_screenshot():
    data = request.json
    logger.info("Taking screenshot with data: %s", data)
    screenshot_dir = get_screenshot_dir()
    ensure_directory_exists(screenshot_dir)
    screenshot_path = os.path.join(screenshot_dir, "screenshot.png")
    
    # Ejemplo: guardar imagen recibida en base64
    if "image_base64" in data:
        import base64
        with open(screenshot_path, "wb") as f:
            f.write(base64.b64decode(data["image_base64"]))
    
    return send_file(
        screenshot_path,
        mimetype='image/png',
        as_attachment=True,
        download_name='screenshot.png'
    )

@screenshot_router.route('/screenshot/<string:screenshot_id>', methods=['GET'])
def get_screenshot(screenshot_id):
    logger.info("Fetching screenshot with ID: %s", screenshot_id)
    screenshot_dir = get_screenshot_dir()
    screenshot_path = os.path.join(screenshot_dir, f"{screenshot_id}.png")
    if not os.path.exists(screenshot_path):
        return jsonify({"error": "Screenshot not found"}), 404
    return send_file(
        screenshot_path,
        mimetype='image/png',
        as_attachment=True,
        download_name=f"{screenshot_id}.png"
    )