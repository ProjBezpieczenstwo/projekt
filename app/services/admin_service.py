import uuid

import requests
from flask import current_app, abort, jsonify

from models import AccessCode, BaseUser, Student, Teacher, TempUser, db


class AdminService:
    @staticmethod
    def get_all_access_codes():
        codes = AccessCode.query.all()
        result = []
        for code in codes:
            creator = BaseUser.query.get(code.created_by)
            code_dict = code.to_dict()
            code_dict['created_by'] = creator.email if creator else 'Unknown'
            result.append(code_dict)
        return jsonify({'access_codes': result}), 200

    @staticmethod
    def generate_access_codes(data, admin_user):
        email = data.get('email')
        number = data.get('number', 1)
        try:
            number = int(number)
        except ValueError:
            abort(400, description='Invalid number of codes')

        code_list = [str(uuid.uuid4()) for _ in range(number)]
        access_codes = [
            AccessCode(code=code, created_by=admin_user.id, email_to=email or None)
            for code in code_list
        ]

        if email:
            try:
                mail_url = f"{current_app.config.get('EMAIL_SERVICE_URL', 'http://127.0.0.1:5001')}/token-email"
                response = requests.post(mail_url, json={
                    "email_receiver": email,
                    "token": "\n".join(code_list)
                })
                if response.status_code != 200:
                    abort(response.status_code, description="Email service error")
            except Exception as e:
                current_app.logger.error(f"Error sending email: {e}")
                abort(500, description=f"Error sending email: {e}")

        db.session.bulk_save_objects(access_codes)
        db.session.commit()
        return jsonify({'message': 'Access codes created'}), 201

    @staticmethod
    def delete_access_code_by_id(code_id):
        code = AccessCode.query.get(code_id)
        if not code:
            abort(404, description='Access code not found')
        db.session.delete(code)
        db.session.commit()
        return jsonify({'message': 'Access code deleted'}), 200

    @staticmethod
    def get_all_users_grouped():
        return jsonify({
            'students': [s.to_dict() for s in Student.query.all()],
            'teachers': [t.to_dict() for t in Teacher.query.all()],
            'temp_users': [u.to_dict() for u in TempUser.query.all()]
        }), 200

    @staticmethod
    def delete_user_by_id(user_id, user_type):
        if user_type == "BaseUser":
            user = BaseUser.query.get(user_id)
        else:
            user = TempUser.query.get(user_id)

        if not user or getattr(user, "role", "") == "admin":
            abort(404, description='User not found or cannot delete admin user')

        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted'}), 200

    @staticmethod
    def delete_temp_user(user_id):
        result = TempUser.query.filter_by(id=user_id).delete()
        db.session.commit()
        if not result:
            abort(404, description='User not found')
        return jsonify({"message": "User deleted"}), 200
