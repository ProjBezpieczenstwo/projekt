from flask import request
from services.admin_service import AdminService
from urls.blueprints import admin
from urls.decorators import jwt_required, jwt_get_user

@admin.route('/access_codes', methods=['GET'])
@jwt_required(role='admin')
def get_access_codes():
    """
    List all access codes
    ---
    tags:
      - Admin
    security:
      - JWT: []
    responses:
      200:
        description: Array of access codes
        schema:
          type: object
          properties:
            access_codes:
              type: array
              items:
                type: object
                properties:
                  id: { type: integer }
                  code: { type: string }
                  email_to: { type: string, nullable: true }
                  created_by: { type: string }
                example:
                  id: 10
                  code: "550e8400-e29b-41d4-a716-446655440000"
                  email_to: "invitee@example.com"
                  created_by: "admin@example.com"
    """
    return AdminService.get_all_access_codes()


@admin.route('/access_codes', methods=['POST'])
@jwt_required(role='admin')
@jwt_get_user()
def create_access_code(admin_user):
    """
    Generate new access codes (optionally emailed)
    ---
    tags:
      - Admin
    security:
      - JWT: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email: { type: string }
            number: { type: integer }
          example:
            email: "invitee@example.com"
            number: 5
    responses:
      201:
        description: Codes generated successfully
        schema:
          type: object
          properties:
            message: { type: string }
        example:
          message: "Access codes created"
      400:
        description: Invalid number of codes
      500:
        description: Error sending email OR internal server error
    """
    data = request.get_json()
    return AdminService.generate_access_codes(data, admin_user)


@admin.route('/access_codes/<int:code_id>', methods=['DELETE'])
@jwt_required(role='admin')
def delete_access_code(code_id):
    """
    Delete an access code by its ID
    ---
    tags:
      - Admin
    security:
      - JWT: []
    parameters:
      - name: code_id
        in: path
        type: integer
        required: true
        description: ID of the code to delete
    responses:
      200:
        description: Access code deleted
        schema:
          type: object
          properties:
            message: { type: string }
        example:
          message: "Access code deleted"
      404:
        description: Access code not found
    """
    return AdminService.delete_access_code_by_id(code_id)


@admin.route('/users', methods=['GET'])
@jwt_required(role='admin')
def get_users():
    """
    Retrieve all users grouped by type
    ---
    tags:
      - Admin
    security:
      - JWT: []
    responses:
      200:
        description: Users grouped in arrays
        schema:
          type: object
          properties:
            students:
              type: array
              items: { type: object }
            teachers:
              type: array
              items: { type: object }
            temp_users:
              type: array
              items: { type: object }
    """
    return AdminService.get_all_users_grouped()


@admin.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required(role='admin')
def delete_user(user_id):
    """
    Delete a user by ID
    ---
    tags:
      - Admin
    security:
      - JWT: []
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the user to delete
      - name: user_type
        in: query
        type: string
        description: "BaseUser or omit for TempUser"
    responses:
      200:
        description: User deleted
        schema:
          type: object
          properties:
            message: { type: string }
        example:
          message: "User deleted"
      404:
        description: User not found or cannot delete admin user
    """
    user_type = request.args.get("user_type")
    return AdminService.delete_user_by_id(user_id, user_type)


@admin.route('/delete_temp_user/<int:user_id>', methods=['GET'])
@jwt_required(role='admin')
def delete_temp(user_id):
    """
    Delete an expired temporary user
    ---
    tags:
      - Admin
    security:
      - JWT: []
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the TempUser
    responses:
      200:
        description: Temporary user deleted
        schema:
          type: object
          properties:
            message: { type: string }
        example:
          message: "User deleted"
      404:
        description: User not found
    """
    return AdminService.delete_temp_user(user_id)
