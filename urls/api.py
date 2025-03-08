from flask import Blueprint, jsonify, request, redirect, send_from_directory
import requests
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from datetime import datetime, timedelta
from sqlalchemy import desc, and_, asc, cast, text, func, Index
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import REGCONFIG
import sys
import requests
import os

SWAGGER_TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../swagger_templates'))

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pdf_generator.lesson_invoice import LessonInvoice
from pdf_generator.pdf_generator import PDFInvoiceGenerator
from models import Teacher, Student, Review, Lesson, Calendar, Invoice, LessonReport, Calendar, Subject, \
    DifficultyLevel, db

api = Blueprint('api', __name__)


def get_user_by_jwt():
    user_id = get_jwt_identity()
    user = Teacher.query.filter_by(id=user_id).first()

    if not user:
        user = Student.query.filter_by(id=user_id).first()

    return user


@api.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Page not found"}), 404


@api.route('/subjects', methods=['GET'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_subjects.yml'))
def get_subjects():
    subjects = Subject.query.all()
    return jsonify({'subjects': [s.to_dict() for s in subjects]}), 200


@api.route('/difficulty-levels', methods=['GET'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_difficulty_levels.yml'))
def get_difficulty_levels():
    difficulty_levels = DifficultyLevel.query.all()
    return jsonify({'difficulty_levels': [d.to_dict() for d in difficulty_levels]}), 200


### Teacher list ###

@api.route('/teacher-list', methods=['GET'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_teacher.yml'))
@jwt_required()
def get_teacher_list():
    user = get_user_by_jwt()
    subject = request.args.get('subject')
    difficulty_id = request.args.get('difficulty_id')

    if not user:
        return jsonify({'message': 'User not found'}), 401

    if subject and difficulty_id:
        teachers = Teacher.query.filter(Teacher.subject_ids.match(subject),
                                        Teacher.difficulty_level_ids.match(difficulty_id)).all()
    elif subject:
        teachers = Teacher.query.filter(Teacher.subject_ids.match(subject)).all()
    elif difficulty_id:
        teachers = Teacher.query.filter(Teacher.difficulty_level_ids.match(difficulty_id)).all()
    else:
        teachers = Teacher.query.all()

    if teachers:
        teacher_list = [teacher.to_dict() for teacher in teachers]

        return jsonify({'teacher_list': teacher_list}), 200
    else:
        return jsonify({'message': 'Teachers not found'}), 404


### End of teacher list ###

@api.route('/teacher-update', methods=['PUT'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'update_teacher.yml'))
@jwt_required()
def update_teacher():
    user = get_user_by_jwt()

    data = request.get_json()
    subject_ids = data.get('subject_ids')
    difficulty_level_ids = data.get('difficulty_ids')
    hourly_rate = data.get('hourly_rate')

    if not user:
        return jsonify({'message': 'User not found'}), 401

    if user.role != 'teacher':
        return jsonify({'message': 'User can not be a student'}), 400

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


### Reviews ###

@api.route('/teacher-reviews', methods=['GET'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_reviews.yml'))
@jwt_required()
def get_reviews():
    user = get_user_by_jwt()

    if not user:
        return jsonify({'message': 'User not found'}), 401

    reviews = Review.query.all()
    reviews_list = [r.to_dict() for r in reviews]

    return jsonify(reviews=reviews_list), 200


@api.route('/teacher-reviews/<int:teacher_id>', methods=['GET'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_reviews_by_id.yml'))
@jwt_required()
def get_reviews_by_id(teacher_id):
    user = get_user_by_jwt()

    if not user:
        return jsonify({'message': 'User not found'}), 401

    try:
        teacher_id = int(teacher_id)
    except ValueError:
        return jsonify({'message': 'Teacher id must be an integer'}), 400

    teacher = Teacher.query.filter_by(id=teacher_id)

    if not teacher:
        return jsonify({'message': 'Teacher not found'}), 404

    reviews = Review.query.filter_by(teacher_id=teacher_id).all()
    reviews_list = [r.to_dict() for r in reviews]

    return jsonify(reviews=reviews_list), 200


@api.route('/teacher-reviews/<int:teacher_id>', methods=['POST'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'add_review.yml'))
@jwt_required()
def add_review(teacher_id):
    user = get_user_by_jwt()

    if not user:
        return jsonify({'message': 'User not found'}), 401

    if user.role != 'student':
        return jsonify({'message': 'User can not be a teacher'}), 400

    lessons = Lesson.query.filter_by(teacher_id=teacher_id, student_id=user.id).first()

    if not lessons:
        return jsonify({'message': 'Student had no lessons with the teacher'}), 400

    data = request.get_json()

    rating = data.get('rating')
    comment = data.get('comment')

    if not rating:
        return jsonify({'message': 'Rating must be provided'}), 400

    if rating < 0 or rating > 5:
        return jsonify({'message': 'Rating must be between values 0 and 5'}), 400

    new_review = Review(teacher_id=teacher_id, student_id=user.id, rating=rating, comment=comment)

    db.session.add(new_review)
    db.session.commit()

    if not comment:
        comment = ""

    return jsonify({"message": "Review created successfully."}), 200


@api.route('/teacher-reviews/<int:teacher_id>', methods=['DELETE'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'delete_review.yml'))
@jwt_required()
def delete_review(teacher_id):
    user = get_user_by_jwt()

    if not user:
        return jsonify({'message': 'User not found'}), 401

    if user.role != 'student':
        return jsonify({'message': 'User can not be a teacher'}), 400

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
@jwt_required()
def add_lesson():
    user = get_user_by_jwt()

    if not user:
        return jsonify({'message': 'User not found'}), 401

    if user.role != 'student':
        return jsonify({'message': 'User can not be a teacher'}), 400

    data = request.get_json()
    teacher_id = data.get('teacher_id')
    subject_id = data.get('subject_id')
    difficulty_level_id = data.get('difficulty_id')
    date = data.get('date')

    if not subject_id:
        return jsonify({'message': 'Subject must be provided'}), 400

    try:
        subject_id = int(subject_id)
    except ValueError:
        return jsonify({'message': 'Subject id must be an integer'}), 400

    subject = Subject.query.filter_by(id=subject_id).first()

    if not subject:
        return jsonify({'message': 'Subject not found'}), 404

    if not difficulty_level_id:
        return jsonify({'message': 'Difficulty level must be provided'}), 400

    try:
        difficulty_level_id = int(difficulty_level_id)
    except ValueError:
        return jsonify({'message': 'Difficulty level id must be an integer'}), 400

    difficulty_level = Subject.query.filter_by(id=difficulty_level_id).first()

    if not difficulty_level:
        return jsonify({'message': 'Difficulty level not found'}), 404

    if not date:
        return jsonify({'message': 'Date must be provided'}), 400

    try:
        date = datetime.strptime(date, "%d/%m/%Y %H:%M")
    except ValueError:
        return jsonify({'message': 'Date must be in format %d/%m/%Y %H:%M'}), 400

    try:
        teacher_id = int(teacher_id)
    except ValueError:
        return jsonify({'message': 'Teacher id must be an integer'}), 400

    teacher = Teacher.query.filter_by(id=teacher_id).first()

    if not teacher:
        return jsonify({'message': 'Teacher not found'}), 404

    calendar = Calendar.query.filter_by(teacher_id=teacher_id).first()

    if not calendar:
        return jsonify({'message': 'Teacher does not hav a calendar set'}), 400

    if date < datetime.utcnow():
        return jsonify({'message': 'Lesson time must be in the future'}), 400

    if date.isoweekday() not in set(map(int, calendar.working_days.replace("{", "").replace("}", "").split(','))):
        return jsonify({'message': 'Teacher does not work on this weekday'}), 400

    if not (calendar.available_from <= date.time() and (date + timedelta(hours=1)).time() <= calendar.available_until):
        return jsonify({'message': 'Teacher does not work in this hours'}), 400

    if subject_id not in set(map(int, teacher.subject_ids.replace("{", "").replace("}", "").split(','))):
        return jsonify({'message': 'Teacher does not teach this subject'}), 400

    if difficulty_level_id not in set(
            map(int, teacher.difficulty_level_ids.replace("{", "").replace("}", "").split(','))):
        return jsonify({'message': 'Teacher does not teach on this difficulty level'}), 400

    if Lesson.query.filter_by(teacher_id=teacher_id, date=date).first():
        return jsonify({'message': 'Lesson with this teacher is already booked for this date'}), 400

    if Lesson.query.filter_by(student_id=user.id, date=date).first():
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

    email_service_url = "http://host.docker.internal:5001/send-email"

    # Email the student
    email_payload = {
        "email_receiver": user.email,
        "subject": f"Lesson has been scheduled",
        "body": (
            f"Dear {user.name},\n\n"
            f"Your lesson with {teacher.name} has been successfully scheduled.\n\n"
            f"Date: {date.strftime('%Y-%m-%d')}"
            "Best regards,\n"
            "Your Teaching Service Team"
        ),
    }
    requests.post(email_service_url, json=email_payload)

    # Email the teacher
    email_payload = {
        "email_receiver": teacher.email,
        "subject": f"Lesson has been scheduled",
        "body": (
            f"Dear {teacher.name},\n\n"
            f"Your lesson with {user.name} has been successfully scheduled.\n\n"
            f"Date: {date.strftime('%Y-%m-%d')}"
            "Best regards,\n"
            "Your Teaching Service Team"
        ),
    }

    requests.post(email_service_url, json=email_payload)

    return jsonify({'message': 'Lesson created'}), 201


@api.route('/lesson', methods=['GET'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_lesson.yml'))
@jwt_required()
def get_lesson():
    user = get_user_by_jwt()
    status = request.args.get('status')
    lessons = None

    if not user:
        return jsonify({'message': 'User not found'}), 401

    if status:
        if status in ['scheduled', 'completed']:
            if user.role == 'student':
                lessons = Lesson.query.filter_by(student_id=user.id, status=status).all()
            elif user.role == 'teacher':
                lessons = Lesson.query.filter_by(teacher_id=user.id, status=status).all()
        else:
            return jsonify({'message': 'Invalid status'}), 400
    else:
        if user.role == 'student':
            lessons = Lesson.query.filter_by(student_id=user.id).all()
        elif user.role == 'teacher':
            lessons = Lesson.query.filter_by(teacher_id=user.id).all()

    if not lessons:
        return jsonify({'message': 'No lessons found'}), 400

    lesson_list = [lesson.to_dict() for lesson in lessons]

    return jsonify(lesson_list=lesson_list), 200


@api.route('/lesson/<int:teacher_id>', methods=['GET'])
# @swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_lesson_by_id.yml'))
@jwt_required()
def get_lesson_by_id(teacher_id):
    user = get_user_by_jwt()

    if not user:
        return jsonify({'message': 'User not found'}), 401

    try:
        teacher_id = int(teacher_id)
    except ValueError:
        return jsonify({'message': 'Teacher id must be an integer'}), 400

    teacher = Teacher.query.filter_by(id=teacher_id).first()

    if not teacher:
        return jsonify({'message': 'Teacher not found'}), 404

    lessons = Lesson.query.filter_by(teacher_id=teacher_id).all()

    if not lessons:
        return jsonify({'message': 'No lessons found'}), 400

    lesson_list = [lesson.to_dict() for lesson in lessons]

    return jsonify(lesson_list=lesson_list), 200


### End of lessons ###


### Invoices ###

BASE_DIR = os.path.join(os.path.dirname(__file__), "../static_invoices")
BASE_DIR = os.path.abspath(BASE_DIR)


@api.route('/generated-invoice-pdf/<filename>', methods=['GET'])
def get_pdf(filename):
    try:
        return send_from_directory(BASE_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 400


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../static_invoices"))


def generate_and_send_invoice(invoice_id):
    try:
        # Pobranie danych z bazy danych
        invoice = Invoice.query.filter_by(id=invoice_id).first()
        if not invoice:
            return jsonify({"error": "Invoice not found"}), 404

        lesson = Lesson.query.filter_by(id=invoice.lesson_id).first()
        if not lesson:
            return jsonify({"error": "Lesson not found"}), 404

        student = Student.query.filter_by(id=lesson.student_id).first()
        if not student:
            return jsonify({"error": "Student not found"}), 404

        teacher = Teacher.query.filter_by(id=lesson.teacher_id).first()
        if not teacher:
            return jsonify({"error": "Teacher not found"}), 404

        subject = Subject.query.filter_by(id=lesson.subject_id).first()
        if not subject:
            return jsonify({"error": "Subject not found"}), 404

        # Tworzenie obiektu LessonInvoice
        lesson_invoice = LessonInvoice(
            invoice_id=invoice.id,
            lesson_id=lesson.id,
            student_name=student.name,
            student_email=student.email,
            teacher_name=teacher.name,
            teacher_email=teacher.email,
            subject=subject.name,
            lesson_date=lesson.date,
            price=invoice.price,
            vat_rate=invoice.vat_rate,
            issue_date=invoice.created_at
        )

        generator = PDFInvoiceGenerator()
        generator.create_invoice(lesson_invoice)

        # `PDFInvoiceGenerator`
        pdf_filename = f"invoice_{invoice_id}.pdf"
        pdf_url = f"http://host.docker.internal:5000/api/generated-invoice-pdf/{pdf_filename}"

        email_service_url = "http://host.docker.internal:5001/send-email"
        email_payload = {
            "email_receiver": student.email,
            "subject": f"Invoice #{invoice_id}",
            "body": (
                f"Dear {student.name},\n\n"
                "Attached is the invoice for your recent lesson.\n\n"
                "Best regards,\n"
                "Your Teaching Service Team"
            ),
            "pdf_path": pdf_url
        }

        response = requests.post(email_service_url, json=email_payload)

        # Obsługa odpowiedzi z mikroserwisu
        if response.status_code == 200:
            return jsonify({
                "message": f"Invoice PDF generated and sent to {student.email}.",
                "invoice_data": lesson_invoice.to_dict()
            }), 200
        else:
            return jsonify({
                "error": f"Failed to send email: {response.json().get('error', 'Unknown error')}"
            }), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/invoice', methods=['POST'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'add_invoice.yml'))
@jwt_required()
def add_invoice():
    user = get_user_by_jwt()

    if not user:
        return jsonify({'message': 'User not found'}), 401

    if user.role != 'student':
        return jsonify({'message': 'User can not be a teacher'}), 400

    data = request.get_json()

    lesson_id = data.get('lesson_id')

    lesson = Lesson.query.filter_by(id=lesson_id).first()
    if not lesson:
        return jsonify({'message': 'Lesson not found'}), 400

    invoice = Invoice.query.filter_by(lesson_id=lesson_id).first()

    if invoice:
        return jsonify({'message': 'Lesson already invoiced'}), 400

    new_invoice = Invoice(lesson_id=lesson_id, price=lesson.price)

    db.session.add(new_invoice)
    db.session.commit()

    generate_and_send_invoice(new_invoice.id)

    return jsonify({'message': 'Invoice created'}), 201


# Necassary endpoint used by the email service, not
# meant to be used by external programs/services


### End of invoices ###


### Reports ###

@api.route('/report', methods=['POST'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'add_report.yml'))
@jwt_required()
def add_report():
    user = get_user_by_jwt()

    if not user:
        return jsonify({'message': 'User not found'}), 401

    if user.role != 'teacher':
        return jsonify({'message': 'User can not be a student'}), 400

    data = request.get_json()
    lesson_id = data.get('lesson_id')
    comment = data.get('comment')
    homework = data.get('homework')
    progress_rating = data.get('progress_rating')

    if not lesson_id:
        return jsonify({'message': 'Lesson id not provided'}), 400

    try:
        lesson_id = int(lesson_id)
    except ValueError:
        return jsonify({'message': 'Lesson id must be an integer'}), 400

    lesson = Lesson.query.filter_by(id=lesson_id).first()

    if not lesson:
        return jsonify({'message': 'Lesson not found'}), 404

    if user.id != lesson.teacher_id:
        return jsonify({'message': 'Teacher does not belong to this lesson and cannot create report'}), 400

    if lesson.date + timedelta(hours=1) > datetime.now():
        return jsonify({'message': 'Report cannot be created before the end of the lesson'}), 400

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

    db.session.query(Lesson).filter_by(id=lesson_id).update({'is_reported': True})
    db.session.add(new_report)
    db.session.commit()

    return jsonify({'message': 'Report created'}), 201


@api.route('/report', methods=['GET'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_report.yml'))
@jwt_required()
def get_report():
    user = get_user_by_jwt()
    reports = None

    if not user:
        return jsonify({'message': 'User not found'}), 401

    if user.role == 'student':
        reports = LessonReport.query.filter_by(student_id=user.id).all()
    elif user.role == 'teacher':
        reports = LessonReport.query.filter_by(teacher_id=user.id).all()

    if not reports:
        return jsonify({'message': 'No reports found'}), 400

    report_list = []
    for report in reports:
        report_list.append(
            {"student_name": Student.query.filter_by(id=report.student_id).first().name,
             "teacher_name": Teacher.query.filter_by(id=report.teacher_id).first().name,
             "subject": Lesson.query.filter_by(id=report.lesson_id).first().subject_id,
             "date": Lesson.query.filter_by(id=report.lesson_id).first().date.strftime("%d/%m/%Y %H:%M"),
             "homework": report.homework,
             "progress_rating": report.progress_rating,
             "comment": report.comment,
             }
        )

    return jsonify({'report_list': report_list}), 200


@api.route('/report/<int:lesson_id>', methods=['GET'])
# @swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_report.yml'))
@jwt_required()
def get_report_by_lesson_id(lesson_id):
    user = get_user_by_jwt()

    if not user:
        return jsonify({'message': 'User not found'}), 401

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


@api.route('/calendar', methods=['POST'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'add_calendar.yml'))
@jwt_required()
def add_calendar():
    user = get_user_by_jwt()

    if not user:
        return jsonify({'message': 'User not found'}), 401

    if user.role != 'teacher':
        return jsonify({'message': 'User can not be a student'}), 400

    data = request.get_json()

    available_from = data.get('available_from')
    available_until = data.get('available_until')
    working_days = data.get('working_days')

    if not available_from or not available_until or not working_days:
        return jsonify({'message': 'Available dates or hours not provided'}), 400

    try:
        available_from = datetime.strptime(available_from, '%H:%M').time()
        available_until = datetime.strptime(available_until, '%H:%M').time()
    except ValueError:
        return jsonify({'message': 'Available hours are not in %H:%M format'}), 400

    try:
        working_days = list(map(int, working_days))
    except ValueError:
        return jsonify(
            {'message': 'Wrong type of working days, expected integers between 1 (Monday) and 7 (Sunday)'}), 400

    if not all(0 < d < 8 for d in working_days):
        return jsonify(
            {'message': 'Wrong value of working days, expected integers between 1 (Monday) and 7 (Sunday)'}), 400

    new_calendar = Calendar(
        teacher_id=user.id,
        available_from=available_from,
        available_until=available_until,
        working_days=working_days
    )

    db.session.add(new_calendar)
    db.session.commit()

    return jsonify({'message': 'Calendar created'}), 201


@api.route('/calendar/<int:teacher_id>', methods=['GET'])
@swag_from(os.path.join(SWAGGER_TEMPLATE_DIR, 'get_calendar.yml'))
@jwt_required()
def get_calendar(teacher_id):
    user = get_user_by_jwt()

    if not user:
        return jsonify({'message': 'User not found'}), 401

    calendar = Calendar.query.filter_by(teacher_id=teacher_id).first()

    if not calendar:
        return jsonify({'message': 'Calendar not found'}), 404

    return jsonify(calendar.to_dict()), 200


### End of calendars ###


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


def update_lesson_status_helper():
    response = requests.post("http://localhost:5000/api/update-lesson-status")
    return response.json(), response.status_code
