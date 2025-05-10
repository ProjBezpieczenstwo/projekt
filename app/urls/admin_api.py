from flask import request

from services.admin_service import AdminService
from urls.decorators import jwt_required, jwt_get_user
from urls.blueprints import admin


@admin.route('/access_codes', methods=['GET'])
@jwt_required(role='admin')
def get_access_codes():
    return AdminService.get_all_access_codes()


@admin.route('/access_codes', methods=['POST'])
@jwt_required(role='admin')
@jwt_get_user()
def create_access_code(admin_user):
    data = request.get_json()
    return AdminService.generate_access_codes(data, admin_user)


@admin.route('/access_codes/<int:code_id>', methods=['DELETE'])
@jwt_required(role='admin')
def delete_access_code(code_id):
    return AdminService.delete_access_code_by_id(code_id)


@admin.route('/users', methods=['GET'])
@jwt_required(role='admin')
def get_users():
    return AdminService.get_all_users_grouped()


@admin.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required(role='admin')
def delete_user(user_id):
    user_type = request.args.get("user_type")
    return AdminService.delete_user_by_id(user_id, user_type)


@admin.route('/delete_temp_user/<int:user_id>', methods=['GET'])
@jwt_required(role='admin')
def delete_temp(user_id):
    return AdminService.delete_temp_user(user_id)
