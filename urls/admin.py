import uuid

import requests
from flask import Blueprint, jsonify, request, current_app
from helper import jwt_required, jwt_get_user
from models import Teacher, Student, db, BaseUser, TempUser, AccessCode

admin = Blueprint('admin', __name__)


# Endpoint do pobierania listy access codes
@admin.route('/access_codes', methods=['GET'])
@jwt_required(role='admin')
def get_access_codes():
    codes = AccessCode.query.all()
    access_codes_data = []

    for code in codes:
        admin_user = BaseUser.query.get(code.created_by)

        code_dict = {
            'id': code.id,
            'code': code.code,
            'created_at': code.created_at.isoformat(),
            'expires_at': code.expires_at.isoformat(),
            'created_by': admin_user.email if admin_user else 'Unknown',
            'email_to': code.email_to
        }

        access_codes_data.append(code_dict)

    return jsonify({'access_codes': access_codes_data}), 200


# Endpoint do generowania nowego access code (opcjonalnie wysyłamy e-mail)
@admin.route('/access_codes', methods=['POST'])
@jwt_required(role='admin')
@jwt_get_user()
def create_access_code(admin_user):
    data = request.get_json()
    email = data.get('email')  # opcjonalne pole
    # Generujemy unikalny kod (możesz zastosować inny algorytm)
    new_code = str(uuid.uuid4())
    if email:
        access_code = AccessCode(code=new_code, created_by=admin_user.id, email_to=email)
        try:
            # Zakładamy, że endpoint usługi mailowej jest dostępny pod adresem skonfigurowanym w konfiguracji
            mail_url = current_app.config.get("EMAIL_SERVICE_URL", "http://127.0.0.1:5001") + "/token-email"
            response = requests.post(mail_url, json={"email_receiver": email, "token": new_code})
            # Możesz obsłużyć response, jeśli potrzebujesz
            if response.status_code != 200:
                return jsonify(response.json()), 500
        except Exception as e:
            current_app.logger.error(f"Error sending email: {e}")
            return jsonify({"message": f"Error sending email: {e}"}), 500
    else:
        access_code = AccessCode(code=new_code, created_by=admin_user.id, email_to="Not provided")
    db.session.add(access_code)
    db.session.commit()
    return jsonify({'message': 'Access code created', 'access_code': access_code.to_dict()}), 201


# Endpoint do usuwania access code
@admin.route('/access_codes/<int:code_id>', methods=['DELETE'])
@jwt_required(role='admin')
def delete_access_code(code_id):
    code = AccessCode.query.get(code_id)
    if not code:
        return jsonify({'message': 'Access code not found'}), 404
    db.session.delete(code)
    db.session.commit()
    return jsonify({'message': 'Access code deleted'}), 200


# Endpoint do pobierania użytkowników (podzielonych na grupy)
@admin.route('/users', methods=['GET'])
@jwt_required(role='admin')
def get_all_users():
    students = Student.query.all()
    teachers = Teacher.query.all()
    temp_users = TempUser.query.all()
    return jsonify({
        'students': [s.to_dict() for s in students],
        'teachers': [t.to_dict() for t in teachers],
        'temp_users': [u.to_dict() for u in temp_users]
    }), 200


# Endpoint do usuwania użytkownika (student, teacher, tempUser)
@admin.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required(role='admin')
def delete_user(user_id):
    user = BaseUser.query.get(user_id) or TempUser.query.get(user_id)
    if not user or user.role == 'admin':
        return jsonify({'message': 'User not found or cannot delete admin user'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200


@admin.route('/delete_temp_user/<int:user_id>', methods=['GET'])
def delete_temp_user(user_id):
    TempUser.query().filter_by(id=user_id).delete()
    db.session.commit()
    return jsonify({"message": "Magic"}), 200
