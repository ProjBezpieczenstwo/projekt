from flask import jsonify

from models import Subject, \
    DifficultyLevel


class DataService:
    @staticmethod
    def get_subjects():
        subjects = Subject.query.all()
        return jsonify({'subjects': [s.to_dict() for s in subjects]}), 200

    @staticmethod
    def get_difficulty_levels():
        difficulty_levels = DifficultyLevel.query.all()
        return jsonify({'difficulty_levels': [d.to_dict() for d in difficulty_levels]}), 200
