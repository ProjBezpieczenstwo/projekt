from flask import jsonify, send_file

from models import Lesson, Calendar, db, WeekDay
from pdf_generator import PDFLessonPlanGenerator


class CalendarService:
    @staticmethod
    def get_calendar_for_teacher(teacher_id):
        calendar = Calendar.query.filter_by(teacher_id=teacher_id).all()
        result = []
        for cal in calendar:
            weekday = WeekDay.query.get(cal.weekday_id)
            available_from_hour = cal.available_from
            available_until_hour = cal.available_until
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
        return abort(400, description="No calendar found.")

    @staticmethod
    def calendar_create_get(user):
        calendars = Calendar.query.filter_by(teacher_id=user.id).all()
        if not calendars:
            return abort(404, description="Calendar not found.")
        calendar_list = [calendar.to_dict() for calendar in calendars]
        return jsonify(calendar_list=calendar_list), 200

    @staticmethod
    def calendar_create_post(user, data):
        teacher_id = user.id
        request_model = data.get('days')

        for entry in request_model:
            day = entry.get('day')
            available_from = int(entry.get('available_from'))
            available_until = int(entry.get('available_until'))
            if available_from >= available_until:
                return abort(400, description=f'Start time must be before end time for day {day}.')
            elif available_from < 16 or available_until > 22:
                return abort(400, description=f'Invalid time format for day {day}.')

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

    @staticmethod
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
