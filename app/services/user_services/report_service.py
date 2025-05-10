from flask import jsonify

from helper import get_object_or_404
from models import Teacher, Student, Lesson, LessonReport, db


class ReportService:
    @staticmethod
    def add_report(user, data):
        lesson_id = data.get('lesson_id')
        comment = data.get('comment')
        homework = data.get('homework')
        progress_rating = data.get('progress_rating')

        lesson = get_object_or_404(Lesson, lesson_id)
        if not isinstance(lesson, Lesson):
            return lesson

        if user.id != lesson.teacher_id:
            return abort(400, description='Teacher does not belong to this lesson and cannot create report')

        if not progress_rating:
            return abort(400, description='Rating must be provided')

        try:
            progress_rating = int(progress_rating)
        except ValueError:
            return abort(400, description='Progress rating must be an integer')

        if progress_rating < 0 or progress_rating > 5:
            return abort(400, description='Rating must be between values 0 and 5')

        if lesson.is_reported:
            return abort(400, description='Lesson is already reported')

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

    @staticmethod
    def get_report_by_lesson_id(user, lesson_id):
        report = LessonReport.query.filter_by(lesson_id=lesson_id).first()
        if not report:
            return abort(400, description='No reports found')

        if not (report.teacher_id == user.id or report.student_id == user.id):
            return abort(400, description='You are not authorized to view this report')

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
