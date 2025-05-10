from flask import request

from services.auth_service import AuthService
from urls.decorators import jwt_required, jwt_get_user
from urls.blueprints import auth


@auth.route('/user/<int:user_id>', methods=['GET'])
@jwt_required(role='admin')
def get_user(user_id):
    return AuthService.get_user(user_id)


@auth.route('/user', methods=['GET'])
@jwt_required()
@jwt_get_user()
def user_credentials(user):
    return AuthService.credentials(user)


@auth.route('/update/<int:user_id>', methods=['POST'])
@jwt_required(role='admin')
def update_admin(user_id):
    data = request.get_json()
    return AuthService.update_admin(user_id, data)


@auth.route('/update', methods=['POST'])
@jwt_required()
@jwt_get_user()
def update(user):
    data = request.get_json()
    return AuthService.updater_user(user, data)


@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    return register(data, is_test=False)


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    return AuthService.login(data)


@auth.route('/confirm/<auth_key>', methods=['GET'])
def check_auth_key(auth_key):
    return AuthService.check_auth_key(auth_key)


@auth.route('/test/register', methods=['POST'])
def test_register():
    data = request.get_json()
    return AuthService.register(data, is_test=True)
