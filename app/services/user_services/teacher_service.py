from flask import jsonify, request

from helper import get_object_or_404
from models import Teacher, Calendar, Subject, \
    DifficultyLevel, db


class TeacherService:
    @staticmethod
    def get_teacher_details(teacher_id):
        teacher = get_object_or_404(Teacher, teacher_id)
        if not isinstance(teacher, Teacher):
            return teacher
        calendar_entries = Calendar.query.filter_by(teacher_id=teacher.id).all()
        available_hours = [entry.to_dict() for entry in calendar_entries] if calendar_entries else []
        teacher_data = teacher.to_dict()
        teacher_data['available_hours'] = available_hours
        return jsonify({'teacher': teacher_data}), 200

    @staticmethod
    def get_teacher_list(page):
        filters = []

        subject = request.args.get('subject')
        difficulty_id = request.args.get('difficulty_id')
        name = request.args.get('name')

        if subject:
            filters.append(Teacher.subject_ids.match(subject))
        if difficulty_id:
            filters.append(Teacher.difficulty_level_ids.match(difficulty_id))
        if name:
            filters.append(Teacher.name.ilike(f"%{name}%"))
        offset = 0 if page == 0 else page * 20
        limit = offset + 20
        teachers_query = Teacher.query.filter(*filters)
        total_teachers = teachers_query.count()

        teachers = teachers_query.limit(limit).offset(offset).all()
        if not teachers:
            return abort(404, description='Teachers not found')

        return jsonify({
            'total': total_teachers,
            'teacher_list': [teacher.to_dict() for teacher in teachers]
        }), 200

    @staticmethod
    def update_teacher(user, data):
        subject_ids = data.get('subject_ids')
        difficulty_level_ids = data.get('difficulty_ids')
        hourly_rate = data.get('hourly_rate')
        try:
            if subject_ids:
                if all(Subject.query.filter_by(id=int(s)).first() for s in subject_ids):
                    db.session.query(Teacher).filter_by(id=user.id).update({'subject_ids': subject_ids})
                else:
                    return abort(404, description='Subject not found')
        except ValueError:
            return abort(400, description='Subject ids can only contain numbers')

        try:
            if difficulty_level_ids:
                if all(DifficultyLevel.query.filter_by(id=int(s)).first() for s in difficulty_level_ids):
                    db.session.query(Teacher).filter_by(id=user.id).update(
                        {'difficulty_level_ids': difficulty_level_ids})
                else:
                    return abort(404, description='Difficulty level not found')
        except ValueError:
            return abort(400, description='Difficulty levels ids can only contain numbers')

        try:
            if hourly_rate:
                hourly_rate = int(hourly_rate)
                db.session.query(Teacher).filter_by(id=user.id).update({'hourly_rate': hourly_rate})
        except ValueError:
            return abort(400, description='Hourly rate can only be an integer')

        db.session.commit()
        return jsonify({'message': 'Teacher details updated'}), 200
