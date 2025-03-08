from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import REGCONFIG
from sqlalchemy import Index, func, text, cast, literal
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token
from datetime import timedelta

db = SQLAlchemy()


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
        #Hash the password when setting it
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        #Check if the provided password matches the stored hash
        return check_password_hash(self.password_hash, password)

    def generate_jwt(self):
        #Generate JWT token for the user that expires after 10 days
        return create_access_token(identity=str(self.id), expires_delta=timedelta(days=10))


class Student(BaseUser):
    __tablename__ = 'students'
    id = db.Column(None, db.ForeignKey('baseusers.id'), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'student'}


class Teacher(BaseUser):
    __tablename__ = 'teachers'
    id = db.Column(None, db.ForeignKey('baseusers.id'), primary_key=True)

    subject_ids = db.Column(db.String(255), nullable=True)  # Comma-separated subject ids
    difficulty_level_ids = db.Column(db.String(255), nullable=True)  # Comma-separated level ids
    hourly_rate = db.Column(db.Integer, nullable=True)
    bio = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subjects': self.subject_ids,
            'difficulty_levels': self.difficulty_level_ids,
            'bio': self.bio,
            'hourly_rate': self.hourly_rate
        }


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

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'student_id': self.student_id,
            'subject': self.subject_id,
            'date': self.date.strftime("%d/%m/%Y %H:%M"),
            'status': self.status,
            'price': self.price,
            'is_reviewed': self.is_reviewed,
            'is_reported': self.is_reported,
            'difficulty_id' : self.difficulty_level_id,
        }

class Calendar(db.Model):
    __tablename__ = 'calendars'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='CASCADE'), nullable=False)
    available_from = db.Column(db.Time, nullable=False)
    available_until = db.Column(db.Time, nullable=False)
    working_days = db.Column(db.Text, nullable=False)  # List of ISO format weekdays (1-7)

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'available_from': self.available_from.strftime("%H:%M"),
            'available_until': self.available_until.strftime("%H:%M"),
            'working_days': self.working_days
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
            'student_id': self.student_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id', ondelete='CASCADE'), nullable=False)
    price = db.Column(db.Float, nullable=False) 
    vat_rate = db.Column(db.Float, default=23.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

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
