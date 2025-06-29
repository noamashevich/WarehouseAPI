from flask import Blueprint, request, jsonify
from app.services import add_truck_service, add_package_service, assign_packages_to_truck_service

api = Blueprint('routes', __name__)

@api.route('/add-truck', methods=['POST'])
def add_truck():
    data = request.get_json()
    result = add_truck_service(data)
    return jsonify(result["body"]), result["status"]

@api.route('/add-package', methods=['POST'])
def add_package():
    data = request.get_json()
    result = add_package_service(data)
    return jsonify(result["body"]), result["status"]

@api.route('/assign-truck', methods=['POST'])
def assign_truck():
    data = request.get_json()
    result = assign_packages_to_truck_service(data.get("package_ids", []))
    return jsonify(result["body"]), result["status"]
