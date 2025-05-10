from datetime import datetime, timedelta

from flask import jsonify
from sqlalchemy import and_

from helper import get_object_or_404
from models import Teacher, Lesson, Subject, \
    DifficultyLevel, db


class LessonService:
    @staticmethod
    def add_lesson(user, data):
        teacher_id = data.get('teacher_id')
        subject = data.get('subject')
        difficulty_level = data.get('difficulty')
        date = data.get('date')
        subject = Subject.query.filter_by(name=str(subject)).first()
        subject_id = subject.id
        difficulty_level = DifficultyLevel.query.filter_by(name=str(difficulty_level)).first()
        difficulty_level_id = difficulty_level.id
        subject = get_object_or_404(Subject, subject_id)
        if not isinstance(subject, Subject):
            return subject

        difficulty = get_object_or_404(DifficultyLevel, difficulty_level_id)
        if not isinstance(difficulty, DifficultyLevel):
            return difficulty

        if not date:
            return abort(400, description='Date must be provided')

        try:
            date = datetime.strptime(date, "%d/%m/%Y %H:%M")
        except ValueError:
            return abort(400, description='Date must be in format %d/%m/%Y %H:%M')

        teacher = get_object_or_404(Teacher, teacher_id)
        if not isinstance(teacher, Teacher):
            return teacher

        if Lesson.query.filter(and_(
                Lesson.student_id == user.id,
                Lesson.date == date,
                Lesson.status != "cancelled"
        )).first():
            return abort(400, description='User has already booked lesson for this date')

        new_lesson = Lesson(
            teacher_id=teacher_id,
            student_id=user.id,
            date=date,
            subject_id=subject_id,
            difficulty_level_id=difficulty_level_id,
            status="scheduled",
            price=teacher.hourly_rate
        )

        db.session.add(new_lesson)
        db.session.commit()

        return jsonify({'message': 'Lesson created'}), 201

    @staticmethod
    def get_lesson(user, status):
        role = user.role
        lessons = None
        if status:
            if status in ['scheduled', 'completed']:
                if role == 'student':
                    lessons = Lesson.query.filter_by(student_id=user.id, status=status).all()
                elif role == 'teacher':
                    lessons = Lesson.query.filter_by(teacher_id=user.id, status=status).all()
            else:
                return abort(400, description='Invalid status')
        else:
            if role == 'student':
                lessons = Lesson.query.filter_by(student_id=user.id).all()
            elif role == 'teacher':
                lessons = Lesson.query.filter_by(teacher_id=user.id).all()

        if not lessons:
            return abort(400, description='No lessons found')

        lesson_list = [lesson.to_dict() for lesson in lessons]

        return jsonify(lesson_list=lesson_list), 200

    @staticmethod
    def get_lesson_by_teacher_id(teacher_id):
        teacher = get_object_or_404(Teacher, teacher_id)
        if not isinstance(teacher, Teacher):
            return teacher

        lessons = Lesson.query.filter_by(teacher_id=teacher.id).all()

        if not lessons:
            return abort(400, description='No lessons found')

        lesson_list = [lesson.to_dict() for lesson in lessons]

        return jsonify(lesson_list=lesson_list), 200

    @staticmethod
    def change_lesson_status(user, lesson_id, data):
        comment = data.get('comment')
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            return abort(400, description='No lesson found')
        if lesson.date + timedelta(hours=1) < datetime.now():
            return abort(400, description='You can not update lesson less than 1 hour before start')
        lesson.status = 'cancelled'
        lesson.cancellation_comment = comment
        lesson.cancelled_by = user.name
        db.session.add(lesson)
        db.session.commit()
        return jsonify({'message': 'Lesson successfully canceled'}), 200
