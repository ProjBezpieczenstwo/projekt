import io
from datetime import date, timedelta

from fpdf import FPDF

from models import DifficultyLevel, Subject, BaseUser


class PDFLessonPlanGenerator:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_font("DejaVu", "", "./font/DejaVuSans.ttf", uni=True)  # Dodajemy czcionkę Unicode
        self.pdf.add_font("DejaVu", "B", "./font/DejaVuSans-Bold.ttf", uni=True)

        self.names = {
            "Monday": "Poniedziałek",
            "Tuesday": "Wtorek",
            "Wednesday": "Środa",
            "Thursday": "Czwartek",
            "Friday": "Piątek",
            "Saturday": "Sobota",
            "Sunday": "Niedziela"
        }

    def generate_pdf(self, weekdays_with_hours, lessons):
        # Przetwarzanie lekcji
        lessons_dto = {
            lesson: (
                DifficultyLevel.query.filter_by(id=lesson.difficulty_level_id).first().name,
                Subject.query.filter_by(id=lesson.subject_id).first().name,
                BaseUser.query.filter_by(id=lesson.student_id).first().name
            )
            for lesson in lessons
        }

        # Grupujemy lekcje według dnia i godziny
        lessons_by_day_hour = {}
        for lesson in lessons_dto:
            lesson_day = lesson.date.date()
            lesson_hour = lesson.date.hour
            if (lesson_day, lesson_hour) not in lessons_by_day_hour:
                lessons_by_day_hour[(lesson_day, lesson_hour)] = []
            lessons_by_day_hour[(lesson_day, lesson_hour)].append(lesson)

        today = date.today()
        start_date = today - timedelta(days=today.weekday())  # weekday(): 0 = Monday
        end_date = start_date + timedelta(days=30)

        current_date = start_date
        while current_date <= end_date:
            self.pdf.add_page()
            self.pdf.set_font('DejaVu', 'B', 14)
            self.pdf.cell(0, 10, f"Plan tygodniowy od {current_date.strftime('%Y-%m-%d')} do {(current_date+timedelta(days=6)).strftime('%Y-%m-%d')}", ln=True, align='C')
            self.pdf.ln(5)

            # Wyciągamy daty dla tego tygodnia
            week_dates = [current_date + timedelta(days=i) for i in range(7)]

            # Nagłówek: kolumny = dni tygodnia
            self.pdf.set_font('DejaVu', 'B', 7)
            self.pdf.cell(25, 10, "Godzina", border=1, align='C')
            for d in week_dates:
                day_label = f"{self.names[d.strftime('%A')]} ({d.strftime('%d.%m')})"
                self.pdf.cell(23, 10, day_label, border=1, align='C')
            self.pdf.ln()

            # Zakładamy zakres godzin od 6 do 22
            for hour in range(6, 22):
                self.pdf.set_font('DejaVu', '', 10)
                self.pdf.cell(25, 10, f"{hour}:00", border=1, align='C')

                for day in week_dates:
                    weekday = day.strftime('%A')
                    date_hour_key = (day, hour)

                    # Sprawdź, czy to dzień pracujący
                    is_working_day = weekday in weekdays_with_hours
                    has_lesson = date_hour_key in lessons_by_day_hour

                    if has_lesson:
                        self.pdf.set_fill_color(0, 255, 0)
                        lessons_text = [
                            "Zajęcia"
                            for _ in lessons_by_day_hour[date_hour_key]
                        ]
                        text = ", ".join(lessons_text)
                    elif is_working_day and weekdays_with_hours[weekday][0] <= hour < weekdays_with_hours[weekday][1]:
                        self.pdf.set_fill_color(200, 200, 200)
                        text = ""
                    else:
                        self.pdf.set_fill_color(255, 255, 255)
                        text = ""

                    self.pdf.cell(23, 10, text[:20] + ("..." if len(text) > 20 else ""), border=1, align='C', fill=True)

                self.pdf.ln()

            current_date += timedelta(days=7)

        pdf_output = io.BytesIO(self.pdf.output(dest='S').encode('latin1'))
        return pdf_output

