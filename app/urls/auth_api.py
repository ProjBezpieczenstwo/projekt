from flask import request
from services.auth_service import AuthService
from urls.decorators import jwt_required, jwt_get_user
from urls.blueprints import auth

@auth.route('/user/<int:user_id>', methods=['GET'])
@jwt_required(role='admin')
def get_user(user_id):
    """
    Retrieve details of a user by ID
    ---
    tags:
      - Auth
    security:
      - JWT: []
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the user to retrieve
    responses:
      200:
        description: User retrieved successfully
        schema:
          type: object
          properties:
            id: { type: integer }
            name: { type: string }
            email: { type: string }
            role: { type: string }
            subject_ids:
              type: array
              items: { type: integer }
            difficulty_level_ids:
              type: array
              items: { type: integer }
            hourly_rate: { type: integer }
            bio: { type: string }
        example:
          id: 1
          name: "Jane Doe"
          email: "jane@example.com"
          role: "teacher"
          subject_ids: [1,3]
          difficulty_level_ids: [2]
          hourly_rate: 60
          bio: "Expert in secondary math"
    """
    return AuthService.get_user(user_id)


@auth.route('/user', methods=['GET'])
@jwt_required()
@jwt_get_user()
def user_credentials(user):
    """
    Get the authenticated user's profile
    ---
    tags:
      - Auth
    security:
      - JWT: []
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: JWT token (Bearer <token>)
    responses:
      200:
        description: Profile retrieved successfully
        schema:
          type: object
          properties:
            id: { type: integer }
            name: { type: string }
            email: { type: string }
            role: { type: string }
          example:
            id: 5
            name: "Student One"
            email: "stud1@example.com"
            role: "student"
    """
    return AuthService.credentials(user)


@auth.route('/update/<int:user_id>', methods=['POST'])
@jwt_required(role='admin')
def update_admin(user_id):
    """
    Update another user's profile (admin only)
    ---
    tags:
      - Auth
    security:
      - JWT: []
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID of the user to update
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name: { type: string }
            email: { type: string }
            role: { type: string }
          example:
            name: "New Name"
            email: "new@example.com"
            role: "teacher"
    responses:
      200:
        description: User updated successfully OR no changes made
        schema:
          type: object
          properties:
            message: { type: string }
        examples:
          updated:
            value: { message: "User updated successfully" }
          no_changes:
            value: { message: "No changes made" }
      400:
        description: No input data provided
        schema:
          type: object
          properties:
            error: { type: string }
        example:
          error: "No input data provided"
      409:
        description: Email already in use
        schema:
          type: object
          properties:
            error: { type: string }
        example:
          error: "Email already in use"
      500:
        description: Update failed
        schema:
          type: object
          properties:
            error: { type: string }
        example:
          error: "Update failed: <details>"
    """
    data = request.get_json()
    return AuthService.update_admin(user_id, data)


@auth.route('/update', methods=['POST'])
@jwt_required()
@jwt_get_user()
def update(user):
    """
    Update the authenticated user's own profile
    ---
    tags:
      - Auth
    security:
      - JWT: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            current_password: { type: string }
            password: { type: string }
            email: { type: string }
            name: { type: string }
          example:
            current_password: "oldpass"
            password: "newpass"
            email: "updated@example.com"
    responses:
      200:
        description: Profile updated successfully OR no changes made
        schema:
          type: object
          properties:
            message: { type: string }
        examples:
          updated:
            value: { message: "User updated successfully" }
          no_changes:
            value: { message: "No changes made" }
      400:
        description: No input data provided
        schema:
          type: object
          properties:
            error: { type: string }
        example:
          error: "No input data provided"
      401:
        description: Invalid current password
        schema:
          type: object
          properties:
            error: { type: string }
        example:
          error: "Invalid password"
      409:
        description: Email already in use
        schema:
          type: object
          properties:
            error: { type: string }
        example:
          error: "Email already in use"
      500:
        description: Update failed
        schema:
          type: object
          properties:
            error: { type: string }
        example:
          error: "Update failed: <details>"
    """
    data = request.get_json()
    return AuthService.updater_user(user, data)


@auth.route('/register', methods=['POST'])
def register():
    """
    Register a new user (student, teacher, or admin)
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name: { type: string }
            email: { type: string }
            password: { type: string }
            role: { type: string }
            subject_ids:
              type: string
              description: for teachers, e.g. "{1,2}"
            difficulty_ids:
              type: string
              description: for teachers, e.g. "{2,3}"
            hourly_rate: { type: integer }
            teacher_code: { type: string }
            secret: { type: string }
          example:
            name: "John Student"
            email: "js@example.com"
            password: "secure123"
            role: "student"
    responses:
      200:
        description: Registration successful (email verification pending) OR admin/test success
        schema:
          type: object
          properties:
            message: { type: string }
        examples:
          student:
            value: { message: "Verify your email now!" }
          admin:
            value: { message: "Account created" }
      400:
        description: Validation error
        schema:
          type: object
          properties:
            message: { type: string }
        examples:
          missing_fields:
            value: { message: "Name, email, password, and role are required." }
          invalid_email:
            value: { message: "Invalid email format." }
          invalid_role:
            value: { message: "Role must be either 'student' or 'teacher'." }
          email_in_use:
            value: { message: "Email already in use." }
          verify_pending:
            value: { message: "Verify your email address." }
          invalid_code:
            value: { message: "Invalid teacher code" }
      404:
        description: Related resource not found
        schema:
          type: object
          properties:
            message: { type: string }
        examples:
          subject_missing:
            value: { message: "Subject not found" }
          difficulty_missing:
            value: { message: "Difficulty level not found" }
      500:
        description: Server error
        schema:
          type: object
          properties:
            message: { type: string }
        example:
          message: "Internal server error"
    """
    data = request.get_json()
    return AuthService.register(data, is_test=False)


@auth.route('/login', methods=['POST'])
def login():
    """
    Authenticate and receive a JWT
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email: { type: string }
            password: { type: string }
          example:
            email: "js@example.com"
            password: "secure123"
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message: { type: string }
            access_token: { type: string }
            role: { type: string }
        example:
          message: "Login successful."
          access_token: "eyJ0eXAiOiJKV1QiLC..."
          role: "student"
      400:
        description: Missing or invalid credentials
        schema:
          type: object
          properties:
            message: { type: string }
        examples:
          missing:
            value: { message: "Email, password are required." }
          bad_email:
            value: { message: "Invalid email format." }
      401:
        description: Authentication failed
        schema:
          type: object
          properties:
            message: { type: string }
        examples:
          invalid:
            value: { message: "Invalid email or password." }
          verify:
            value: { message: "Verify your email." }
    """
    data = request.get_json()
    return AuthService.login(data)


@auth.route('/confirm/<auth_key>', methods=['GET'])
def check_auth_key(auth_key):
    """
    Verify a user's registration via confirmation key
    ---
    tags:
      - Auth
    parameters:
      - name: auth_key
        in: path
        type: string
        required: true
        description: Confirmation key sent by email
    responses:
      201:
        description: User account activated
        schema:
          type: object
          properties:
            message: { type: string }
        example:
          message: "Student registered successfully."
      400:
        description: Invalid or missing key
        schema:
          type: object
          properties:
            message: { type: string }
        examples:
          bad_link:
            value: { message: "Bad link." }
          invalid:
            value: { message: "Invalid link" }
      500:
        description: Server error
        schema:
          type: object
          properties:
            message: { type: string }
        example:
          message: "Error occurred while creating new user."
    """
    return AuthService.check_auth_key(auth_key)


@auth.route('/test/register', methods=['POST'])
def test_register():
    """
    Register a test user (bypasses email step)
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name: { type: string }
            email: { type: string }
            password: { type: string }
            role: { type: string }
          example:
            name: "Test User"
            email: "test@example.com"
            password: "pass123"
            role: "student"
    responses:
      200:
        description: Test account created successfully
        schema:
          type: object
          properties:
            message: { type: string }
        example:
          message: "Test account created successfully"
      400:
        description: Validation error
        schema:
          type: object
          properties:
            message: { type: string }
        example:
          message: "Name, email, password, and role are required."
      404:
        description: Related resource not found
        schema:
          type: object
          properties:
            message: { type: string }
        example:
          message: "Subject not found"
      500:
        description: Server error
        schema:
          type: object
          properties:
            message: { type: string }
        example:
          message: "Internal server error"
    """
    data = request.get_json()
    return AuthService.register(data, is_test=True)
