from services.user_services.data_service import DataService

from ..blueprints import api


@api.route('/subjects', methods=['GET'])
def get_subjects():
    return DataService.get_subjects()


@api.route('/difficulty-levels', methods=['GET'])
def get_difficulty_levels():
    return DataService.get_difficulty_levels()
