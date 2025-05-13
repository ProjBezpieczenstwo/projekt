from services.user_services.data_service import DataService
from urls.blueprints import api

@api.route('/subjects', methods=['GET'])
def get_subjects():
    """
    List all available subjects
    ---
    tags:
      - Data
    responses:
      200:
        description: Array of subjects
        schema:
          type: object
          properties:
            subjects:
              type: array
              items:
                type: object
                properties:
                  id: { type: integer }
                  name: { type: string }
                example:
                  id: 1
                  name: "Maths"
    """
    return DataService.get_subjects()

@api.route('/difficulty-levels', methods=['GET'])
def get_difficulty_levels():
    """
    List all difficulty levels
    ---
    tags:
      - Data
    responses:
      200:
        description: Array of difficulty levels
        schema:
          type: object
          properties:
            difficulty_levels:
              type: array
              items:
                type: object
                properties:
                  id: { type: integer }
                  name: { type: string }
                example:
                  id: 3
                  name: "Higher Secondary School"
    """
    return DataService.get_difficulty_levels()
