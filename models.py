from datetime import datetime
from datetime import timedelta

from flask import current_app
from flask_jwt_extended import create_access_token
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class WeekDay(db.Model):
    __tablename__ = 'weekday'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }


# Base class for students and teachers
class BaseUser(db.Model):
    __tablename__ = 'baseusers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __mapper_args__ = {
        'polymorphic_identity': 'baseuser',
        'polymorphic_on': 'role'
    }

    def set_password(self, password):
        # Hash the password when setting it
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # Check if the provided password matches the stored hash
        return check_password_hash(self.password_hash, password)

    def generate_jwt(self):
        # Generate JWT token for the user that expires after 10 days
        return create_access_token(identity=str(self.id), expires_delta=timedelta(days=10))

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "created_at": self.created_at.strftime("%d.%m.%Y %H:%M")
        }


class Student(BaseUser):
    __tablename__ = 'students'
    id = db.Column(None, db.ForeignKey('baseusers.id'), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'student'}

    def to_dict(self):
        return super().to_dict()


class Teacher(BaseUser):
    __tablename__ = 'teachers'
    id = db.Column(None, db.ForeignKey('baseusers.id'), primary_key=True)
    subject_ids = db.Column(db.String(255), nullable=True)
    difficulty_level_ids = db.Column(db.String(255), nullable=True)
    hourly_rate = db.Column(db.Integer, nullable=True)
    bio = db.Column(db.Text, nullable=True)

    def to_dict(self):
        current_app.logger.error(f"{get_names_from_ids(self.subject_ids, Subject)}")
        current_app.logger.error(f"{get_names_from_ids(self.difficulty_level_ids, DifficultyLevel)}")
        resp = {**super().to_dict(), **{
            'subjects': get_names_from_ids(self.subject_ids, Subject),
            'difficulty_levels': get_names_from_ids(self.difficulty_level_ids, DifficultyLevel),
            'bio': self.bio,
            'hourly_rate': self.hourly_rate
        }}
        reviews = Review.query.filter_by(teacher_id=self.id).all()
        if reviews:
            total = sum(review.rating for review in reviews)
            resp['avg'] = round(total / len(reviews), 2)
        else:
            resp['avg'] = 0.00
        return resp

    __mapper_args__ = {'polymorphic_identity': 'teacher'}


class Lesson(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    difficulty_level_id = db.Column(db.Integer, db.ForeignKey('difficultyLevels.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # 'scheduled', 'completed', 'cancelled'
    is_reviewed = db.Column(db.Boolean, nullable=False, default=False)
    is_reported = db.Column(db.Boolean, nullable=False, default=False)
    price = db.Column(db.Float, nullable=False)
    cancellation_comment = db.Column(db.String(255), nullable=True)
    cancelled_by = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        data = {
            'id': self.id,
            'teacher_id': Teacher.query.get(self.teacher_id).name,
            'student_id': Student.query.get(self.student_id).name,
            'subject': Subject.query.get(self.subject_id).name,
            'date': self.date.strftime("%d/%m/%Y %H:%M"),
            'status': self.status,
            'price': self.price,
            'is_reviewed': self.is_reviewed,
            'is_reported': self.is_reported,
            'difficulty_id': DifficultyLevel.query.get(self.difficulty_level_id).name
        }
        if self.is_reported:
            data['report'] = LessonReport.query.filter_by(lesson_id=self.id).first().to_dict()
        if self.cancellation_comment:
            data['cancellation_comment'] = self.cancellation_comment
            data['cancelled_by'] = self.cancelled_by
        return data


class Calendar(db.Model):
    __tablename__ = 'calendars'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    weekday_id = db.Column(db.Integer, db.ForeignKey('weekday.id', ondelete='CASCADE'), nullable=False)
    available_from = db.Column(db.Integer, nullable=False)
    available_until = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'weekday_id': self.weekday_id,
            'available_from': self.available_from,
            'available_until': self.available_until
        }


class LessonReport(db.Model):
    __tablename__ = 'lesson_reports'
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    homework = db.Column(db.Text, nullable=False)
    progress_rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'lesson_id': self.lesson_id,
            'student_id': self.student_id,
            'teacher_id': self.teacher_id,
            'homework': self.homework,
            'progress_rating': self.progress_rating,
            'comment': self.comment,
        }


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'student_id': Student.query.get(self.student_id).name,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.strftime("%d.%m.%Y %H:%M") if self.created_at else None
        }


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class DifficultyLevel(db.Model):
    __tablename__ = 'difficultyLevels'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class TempUser(db.Model):
    __tablename__ = 'tempUsers'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    subject_ids = db.Column(db.String(255), nullable=True)
    difficulty_level_ids = db.Column(db.String(255), nullable=True)
    hourly_rate = db.Column(db.Integer, nullable=True)
    bio = db.Column(db.Text, nullable=True)
    expired_at = db.Column(db.DateTime, default=datetime.utcnow() + timedelta(minutes=30))
    auth_key = db.Column(db.String(120))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        if self.role == "Teacher":
            res = {
                "id": self.id,
                "email": self.email,
                "name": self.name,
                "role": self.role,
                "subject_ids": self.subject_ids,
                "difficulty_level_ids": self.difficulty_level_ids,
                "hourly_rate": self.hourly_rate,
                "expired_at": self.expired_at.strftime("%d.%m.%Y %H:%M") if self.expired_at else None,
                "auth_key": self.auth_key
            }
        else:
            res = {
                "id": self.id,
                "email": self.email,
                "name": self.name,
                "role": self.role,
                "expired_at": self.expired_at.strftime("%d.%m.%Y %H:%M") if self.expired_at else None,
                "auth_key": self.auth_key
            }
        return res


class Admin(BaseUser):
    __tablename__ = 'admins'
    id = db.Column(None, db.ForeignKey('baseusers.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'admin'}


class AccessCode(db.Model):
    __tablename__ = 'access_codes'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=14))
    created_by = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    email_to = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'created_at': self.created_at.strftime("%d.%m.%Y %H:%M"),
            'expires_at': self.expires_at.strftime("%d.%m.%Y %H:%M"),
            'created_by': self.created_by,
            'email_to': self.email_to
        }


def get_names_from_ids(id_string, model):
    if not id_string:
        return []
    try:
        id_string = id_string.replace("{", "").replace("}", "")
        ids = [int(i.strip()) for i in id_string.split(',') if i.strip().isdigit()]
        names = db.session.query(model.name).filter(model.id.in_(ids)).all()
        return [name for (name,) in names]
    except Exception as e:
        return []
