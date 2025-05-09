import os
import sys
from datetime import datetime, timedelta

import requests
from flasgger import swag_from
from flask import Blueprint, jsonify, request, send_file
from helper import jwt_required, get_object_or_404, jwt_get_user
from models import Teacher, Student, Review, Lesson, LessonReport, Calendar, Subject, \
    DifficultyLevel, db, WeekDay, TempUser
from pdf_generator import PDFLessonPlanGenerator
from sqlalchemy import and_
SWAGGER_TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../swagger_templates'))

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

api = Blueprint('api', __name__)

### 404 ###
@api.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Page not found"}), 404

### SUBJECTS ###
@api.route('/subjects', methods=['GET'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_subjects.yml'))
def get_subjects():
    subjects = Subject.query.all()
    return jsonify({'subjects': [s.to_dict() for s in subjects]}), 200

### DIFFICULTY-LEVELS ###
@api.route('/difficulty-levels', methods=['GET'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_difficulty_levels.yml'))
def get_difficulty_levels():
    difficulty_levels = DifficultyLevel.query.all()
    return jsonify({'difficulty_levels': [d.to_dict() for d in difficulty_levels]}), 200


### Teacher ###

@api.route('/teacher/<int:teacher_id>', methods=['GET'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_teacher_details.yml'))
@jwt_required()
def get_teacher_details(teacher_id):
    teacher = get_object_or_404(Teacher, teacher_id)
    if not isinstance(teacher, Teacher):
        return teacher
    calendar_entries = Calendar.query.filter_by(teacher_id=teacher.id).all()
    available_hours = [entry.to_dict() for entry in calendar_entries] if calendar_entries else []
    teacher_data = teacher.to_dict()
    teacher_data['available_hours'] = available_hours
    return jsonify({'teacher': teacher_data}), 200


@api.route('/teacher-list/<int:page>', methods=['GET'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_teacher.yml'))
@jwt_required()
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
        return jsonify({'message': 'Teachers not found'}), 404

    return jsonify({
        'total': total_teachers,
        'teacher_list': [teacher.to_dict() for teacher in teachers]
    }), 200


@api.route('/teacher-update', methods=['PUT'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'update_teacher.yml'))
@jwt_required(role='teacher')
@jwt_get_user()
def update_teacher(user):
    data = request.get_json()
    subject_ids = data.get('subject_ids')
    difficulty_level_ids = data.get('difficulty_ids')
    hourly_rate = data.get('hourly_rate')
    try:
        if subject_ids:
            if all(Subject.query.filter_by(id=int(s)).first() for s in subject_ids):
                db.session.query(Teacher).filter_by(id=user.id).update({'subject_ids': subject_ids})
            else:
                return jsonify({'message': 'Subject not found'}), 404
    except ValueError:
        return jsonify({'message': 'Subject ids can only contain numbers'}), 400

    try:
        if difficulty_level_ids:
            if all(DifficultyLevel.query.filter_by(id=int(s)).first() for s in difficulty_level_ids):
                db.session.query(Teacher).filter_by(id=user.id).update({'difficulty_level_ids': difficulty_level_ids})
            else:
                return jsonify({'message': 'Difficulty level not found'}), 404
    except ValueError:
        return jsonify({'message': 'Difficulty levels ids can only contain numbers'}), 400

    try:
        if hourly_rate:
            hourly_rate = int(hourly_rate)
            db.session.query(Teacher).filter_by(id=user.id).update({'hourly_rate': hourly_rate})
    except ValueError:
        return jsonify({'message': 'Hourly rate can only be an integer'}), 400

    db.session.commit()
    return jsonify({'message': 'Teacher details updated'}), 200
### End of teacher ###

### Reviews ###

@api.route('/teacher-reviews', methods=['GET'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_reviews.yml'))
@jwt_required()
def get_reviews():
    reviews = Review.query.all()
    reviews_list = [r.to_dict() for r in reviews]
    return jsonify(reviews=reviews_list), 200


@api.route('/teacher-reviews/<int:teacher_id>', methods=['GET'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_reviews_by_id.yml'))
@jwt_required()
def get_reviews_by_id(teacher_id):
    teacher = get_object_or_404(Teacher, teacher_id)
    if not isinstance(teacher, Teacher):
        return teacher

    reviews = Review.query.filter_by(teacher_id=teacher_id).all()
    reviews_list = [r.to_dict() for r in reviews]

    return jsonify(reviews=reviews_list), 200


@api.route('/add_review', methods=['POST'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'add_review.yml'))
@jwt_required(role='student')
@jwt_get_user()
def add_review(user):
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    rating = data.get('rating')
    rating = int(rating)
    comment = data.get('comment')
    lessons = Lesson.query.filter_by(id=lesson_id).first()

    if not lessons:
        return jsonify({'message': 'Student had no lessons with the teacher'}), 400

    if not rating:
        return jsonify({'message': 'Rating must be provided'}), 400

    if rating < 0 or rating > 5:
        return jsonify({'message': 'Rating must be between values 0 and 5'}), 400

    if not comment:
        comment = ""
    teacher_id = lessons.teacher_id
    lessons.is_reviewed = True
    new_review = Review(teacher_id=teacher_id, student_id=user.id, rating=rating, comment=comment)
    db.session.add(new_review)
    db.session.add(lessons)
    db.session.commit()

    return jsonify({"message": "Review created successfully."}), 200


@api.route('/teacher-reviews/<int:teacher_id>', methods=['DELETE'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'delete_review.yml'))
@jwt_required(role='student')
@jwt_get_user()
def delete_review(user, teacher_id):
    review = Review.query.filter_by(teacher_id=teacher_id, student_id=user.id).first()

    if not review:
        return jsonify({"message": f"Review does not exist"}), 404

    db.session.delete(review)
    db.session.commit()

    return jsonify({"message": "Review deleted successfuly"}), 200


### The end of reviews ###


### Lessons ###
@api.route('/lesson', methods=['POST'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'add_lesson.yml'))
@jwt_required(role='student')
@jwt_get_user()
def add_lesson(user):
    data = request.get_json()
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
        return jsonify({'message': 'Date must be provided'}), 400

    try:
        date = datetime.strptime(date, "%d/%m/%Y %H:%M")
    except ValueError:
        return jsonify({'message': 'Date must be in format %d/%m/%Y %H:%M'}), 400

    teacher = get_object_or_404(Teacher, teacher_id)
    if not isinstance(teacher, Teacher):
        return teacher

    if Lesson.query.filter(and_(
            Lesson.student_id == user.id,
            Lesson.date == date,
            Lesson.status != "cancelled"
    )).first():
        return jsonify({'message': 'User has already booked lesson for this date'}), 400

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


@api.route('/lesson', methods=['GET'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_lesson.yml'))
@jwt_required()
@jwt_get_user()
def get_lesson(user):
    role = user.role
    status = request.args.get('status')
    lessons = None
    if status:
        if status in ['scheduled', 'completed']:
            if role == 'student':
                lessons = Lesson.query.filter_by(student_id=user.id, status=status).all()
            elif role == 'teacher':
                lessons = Lesson.query.filter_by(teacher_id=user.id, status=status).all()
        else:
            return jsonify({'message': 'Invalid status'}), 400
    else:
        if role == 'student':
            lessons = Lesson.query.filter_by(student_id=user.id).all()
        elif role == 'teacher':
            lessons = Lesson.query.filter_by(teacher_id=user.id).all()

    if not lessons:
        return jsonify({'message': 'No lessons found'}), 400

    lesson_list = [lesson.to_dict() for lesson in lessons]

    return jsonify(lesson_list=lesson_list), 200


@api.route('/lesson/<int:teacher_id>', methods=['GET'])
# @swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_lesson_by_id.yml'))
@jwt_required()
def get_lesson_by_id(teacher_id):
    teacher = get_object_or_404(Teacher, teacher_id)
    if not isinstance(teacher, Teacher):
        return teacher

    lessons = Lesson.query.filter_by(teacher_id=teacher.id).all()

    if not lessons:
        return jsonify({'message': 'No lessons found'}), 400

    lesson_list = [lesson.to_dict() for lesson in lessons]

    return jsonify(lesson_list=lesson_list), 200


@api.route('/lesson/<int:lesson_id>', methods=['PUT'])
@jwt_required()
@jwt_get_user()
def change_lesson_status(user,lesson_id):
    data = request.get_json()
    comment = data.get('comment')
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({'message': 'No lesson found'}), 400
    if lesson.date + timedelta(hours=1) < datetime.now():
        return jsonify({'message':'You can not update lesson less than 1 hour before start'}),400
    lesson.status = 'cancelled'
    lesson.cancellation_comment = comment
    lesson.cancelled_by = user.name
    db.session.add(lesson)
    db.session.commit()
    return jsonify({'message' : 'Lesson successfully canceled'}), 200

### End of lessons ###


### Reports ###

@api.route('/report', methods=['POST'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'add_report.yml'))
@jwt_required(role='teacher')
@jwt_get_user()
def add_report(user):
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    comment = data.get('comment')
    homework = data.get('homework')
    progress_rating = data.get('progress_rating')

    lesson = get_object_or_404(Lesson, lesson_id)
    if not isinstance(lesson, Lesson):
        return lesson

    if user.id != lesson.teacher_id:
        return jsonify({'message': 'Teacher does not belong to this lesson and cannot create report'}), 400

    if not progress_rating:
        return jsonify({'message': 'Rating must be provided'}), 400

    try:
        progress_rating = int(progress_rating)
    except ValueError:
        return jsonify({'message': 'Progress rating must be an integer'}), 400

    if progress_rating < 0 or progress_rating > 5:
        return jsonify({'message': 'Rating must be between values 0 and 5'}), 400

    if lesson.is_reported:
        return jsonify({'message': 'Lesson is already reported'}), 400

    if not comment:
        comment = ''

    if not homework:
        homework = ''

    new_report = LessonReport(
        lesson_id=lesson_id,
        comment=comment,
        progress_rating=progress_rating,
        homework=homework,
        student_id=lesson.student_id,
        teacher_id=lesson.teacher_id
    )
    lesson.is_reported = True
    db.session.add(new_report)
    db.session.add(lesson)
    db.session.commit()

    return jsonify({'message': 'Report created'}), 201


@api.route('/report/<int:lesson_id>', methods=['GET'])
# @swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_report.yml'))
@jwt_required()
@jwt_get_user()
def get_report_by_lesson_id(user, lesson_id):
    report = LessonReport.query.filter_by(lesson_id=lesson_id).first()

    if not report:
        return jsonify({'message': 'No reports found'}), 400

    if not (report.teacher_id == user.id or report.student_id == user.id):
        return jsonify({'message': 'You are not authorized to view this report}'}), 400

    report_dict = {
        "student_name": Student.query.filter_by(id=report.student_id).first().name,
        "teacher_name": Teacher.query.filter_by(id=report.teacher_id).first().name,
        "subject": Lesson.query.filter_by(id=report.lesson_id).first().subject_id,
        "date": Lesson.query.filter_by(id=report.lesson_id).first().date.strftime("%d/%m/%Y %H:%M"),
        "homework": report.homework,
        "progress_rating": report.progress_rating,
        "comment": report.comment,
    }

    return jsonify({'report': report_dict}), 200


### End of reports ###


### Calendars ###
@api.route('/calendar/<int:teacher_id>', methods=['GET'])
@jwt_required()
def get_calendar_for_teacher(teacher_id):
    calendar = Calendar.query.filter_by(teacher_id=teacher_id).all()
    result = []
    for cal in calendar:
        weekday = WeekDay.query.get(cal.weekday_id)
        available_from_hour = cal.available_from
        available_until_hour = cal.available_until

        # Generowanie godzin dostępnych między available_from i available_until
        available_hours = []
        current_hour = available_from_hour
        while current_hour < available_until_hour:
            available_hours.append(f"{current_hour:02d}:00")
            current_hour += 1

        result.append({
            'id': cal.id,
            'teacher_id': cal.teacher_id,
            'weekday': weekday.name,
            'available_hours': available_hours  # Lista godzin, np. ["10:00", "11:00"]
        })
    if result:
        return jsonify({'calendar': result}), 200
    return jsonify({'message': 'No calendar found'}), 400


@api.route('/calendar', methods=['POST', 'GET'])
@jwt_required(role='teacher')
@jwt_get_user()
def calendar_create(user):
    if request.method == 'GET':
        calendars = Calendar.query.filter_by(teacher_id=user.id).all()
        if not calendars:
            return jsonify({'message': 'Calendar not found'}), 404
        calendar_list = [calendar.to_dict() for calendar in calendars]
        return jsonify(calendar_list=calendar_list), 200

    data = request.get_json()
    teacher_id = user.id
    request_model = data.get('days')

    for entry in request_model:
        day = entry.get('day')
        available_from = int(entry.get('available_from'))
        available_until = int(entry.get('available_until'))
        if available_from >= available_until:
            return jsonify({
                'message': f'Start time must be before end time for day {day}.'
            }), 400
        elif available_from < 16 or available_until > 22:
            return jsonify({
                'message': f'Invalid time format for day {day}.'
            }), 400

    clear_calendar(teacher_id)

    for entry in request_model:
        day = entry.get('day')
        available_from = int(entry.get('available_from'))
        available_until = int(entry.get('available_until'))
        new_entry = Calendar(
            teacher_id=int(teacher_id),
            weekday_id=int(day),
            available_from=available_from,
            available_until=available_until
        )
        db.session.add(new_entry)

    db.session.commit()
    return jsonify({'message': 'Calendar updated'}), 201


@api.route('/calendar/pdf', methods=['GET'])
@jwt_required(role='teacher')
@jwt_get_user()
def get_calendar_pdf(user):
    calendar = Calendar.query.filter_by(teacher_id=user.id).all()
    lessons = Lesson.query.filter(
        Lesson.teacher_id == user.id,
        Lesson.status == "scheduled"
    ).all()
    weekdays_with_hours = {
        WeekDay.query.filter_by(id=entry.weekday_id).first().name: (entry.available_from, entry.available_until)
        for entry in calendar}
    pdf_gen = PDFLessonPlanGenerator()
    pdf_file = pdf_gen.generate_pdf(weekdays_with_hours, lessons)

    return send_file(
        pdf_file,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"lesson_plan_{user.id}.pdf"
    )


### End of calendars ###

### HELPERS ###

@api.route('/update-lesson-status', methods=['POST'])
def update_lesson_status():
    current_time = datetime.utcnow()
    lessons_to_update = Lesson.query.filter(
        Lesson.date < current_time,
        Lesson.status == 'scheduled'
    ).all()

    for lesson in lessons_to_update:
        lesson.status = 'completed'

    db.session.commit()
    return jsonify({'message': f'Updated {len(lessons_to_update)} lessons'}), 200


@api.route('/delete-expired-temp-users', methods=['GET'])
def delete_expired_temp_users():
    expiration_time = datetime.utcnow()
    db.session.query(TempUser).filter(TempUser.expired_at < expiration_time).delete()


@api.route('/weekdays/all', methods=['GET'])
def weekdays_all():
    weekdays = WeekDay.query.all()
    weekdays_list = [weekday.to_dict() for weekday in weekdays]
    return jsonify(weekdays=weekdays_list), 200

### End of helpers ###

def clear_calendar(teacher_id):
    db.session.query(Calendar).filter(Calendar.teacher_id == teacher_id).delete()
    db.session.commit()


def update_lesson_status_helper():
    response = requests.post("http://localhost:5000/api/update-lesson-status")
    return response.json(), response.status_code


def delete_expired_temp_users_helper():
    response = requests.get("http://localhost:5000/api/delete-expired")
    return response.json(), response.status_code
