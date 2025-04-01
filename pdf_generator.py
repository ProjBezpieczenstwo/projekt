import os
import io
from datetime import date, timedelta
from models import Lesson, DifficultyLevel, Subject, BaseUser
from fpdf import FPDF


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
        # Tworzymy słownik z przetworzonymi danymi lekcji
        lessons_dto = {
            lesson: (
                DifficultyLevel.query.filter_by(id=lesson.difficulty_level_id).first().name,
                Subject.query.filter_by(id=lesson.subject_id).first().name,
                BaseUser.query.filter_by(id=lesson.student_id).first().name
            )
            for lesson in lessons
        }

        # Grupujemy lekcje według dnia
        lessons_by_day = {}
        for lesson in lessons_dto:
            lesson_day = lesson.date.date()
            if lesson_day not in lessons_by_day:
                lessons_by_day[lesson_day] = []
            lessons_by_day[lesson_day].append(lesson)

        start_date = date.today()
        end_date = start_date + timedelta(days=30)

        current_date = start_date
        while current_date <= end_date:
            weekday_name = current_date.strftime("%A")  # Pobieramy nazwę dnia np. "Monday"

            # Sprawdzamy, czy ten dzień jest w planie nauczyciela
            if weekday_name not in weekdays_with_hours:
                current_date += timedelta(days=1)
                continue  # Pomijamy ten dzień, jeśli nie jest pracujący

            self.pdf.add_page()

            # Pobieramy godziny pracy dla danego dnia
            start_hour, end_hour = weekdays_with_hours[weekday_name]

            # Nagłówek strony
            self.pdf.set_font('DejaVu', 'B', 16)
            self.pdf.cell(0, 10, f"Plan Zajęć - {current_date.strftime('%Y-%m-%d')} ({self.names[weekday_name]})", ln=True, align='C')
            self.pdf.ln(5)

            # Nagłówek tabeli
            self.pdf.set_font('DejaVu', 'B', 12)
            self.pdf.cell(30, 10, "Godzina", border=1, align='C')
            self.pdf.cell(0, 10, "Zajęcia", border=1, align='C', ln=True)

            lessons_today = lessons_by_day.get(current_date, [])

            self.pdf.set_font('DejaVu', '', 12)  # Czcionka dla tekstu

            for hour in range(start_hour, end_hour):
                self.pdf.cell(30, 10, f"{hour}:00", border=1, align='C')

                # Filtrujemy lekcje, które są w danej godzinie
                lessons_this_hour = [
                    (lesson, lessons_dto[lesson]) for lesson in lessons_today if lesson.date.hour == hour
                ]

                if lessons_this_hour:
                    self.pdf.set_fill_color(0, 255, 0)  # Czerwone tło dla zajęć
                    lesson_texts = [
                        f"Zajęcia z {student} z przedmiotu {subject} o poziomie trudności {difficulty}"
                        for difficulty, subject, student in [lessons_dto[lesson] for lesson, _ in lessons_this_hour]
                    ]
                    cell_text = "\n".join(lesson_texts)
                else:
                    self.pdf.set_fill_color(255, 255, 255)  # Białe tło dla pustych godzin
                    cell_text = "Wolne"

                self.pdf.multi_cell(0, 10, cell_text, border=1, align='C', fill=True)

            current_date += timedelta(days=1)

        # **📌 Zapisanie pliku do pamięci zamiast na dysk**
        pdf_output = io.BytesIO(self.pdf.output(dest='S'))

        return pdf_output
