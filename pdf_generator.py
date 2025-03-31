import os
from datetime import date, timedelta
from models import Lesson
from fpdf import FPDF


class PDFLessonPlanGenerator:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.names = {"Monday": 0,
                      "Tuesday": 1,
                      "Wednesday": 2,
                      "Thursday": 3,
                      "Friday": 4,
                      "Saturday": 5,
                      "Sunday": 6
                      }
        self.template = list(
            list(f"{hour}:00" for _ in range(7)) for hour in range(8, 23)
        )

    def generate_pdf(self, weekdays_with_hours, lessons):
        lessons_by_day = {}
        for lesson in lessons:
            lesson_day = lesson.date.date()
            weekday_pl = self.names[lesson_day.weekday()]
            # Only include days where the teacher teaches.
            if weekday_pl not in weekdays_with_hours:
                continue
            if lesson_day not in lessons_by_day:
                lessons_by_day[lesson_day] = []
            lessons_by_day[lesson_day].append(lesson)

        # Sort the days chronologically
        days = sorted(lessons_by_day.keys())

        # For each teaching day, generate a lesson plan page.
        for day in days:
            self.pdf.add_page()
            weekday_pl = self.names[day.weekday()]
            # Page header for the day.
            self.pdf.set_font('DejaVu', 'B', 16)
            self.pdf.cell(0, 10, f"Plan Zajęć - {day.strftime('%Y-%m-%d')} ({weekday_pl})", ln=True, align='C')
            self.pdf.ln(5)

            # Table header: "Godzina" (Hour) and "Zajęcia" (Lesson)
            self.pdf.set_font('DejaVu', 'B', 12)
            self.pdf.cell(30, 10, "Godzina", border=1, align='C')
            self.pdf.cell(0, 10, "Zajęcia", border=1, align='C', ln=True)

            self.pdf.set_font('DejaVu', '', 12)
            # Determine the teacher's working hours for this day.
            working_hours = weekdays_with_hours.get(weekday_pl)
            if isinstance(working_hours, tuple):
                start_hour, end_hour = working_hours
            else:
                start_hour, end_hour = (0, 0)

            # For each hour in the teacher's schedule, indicate if there is a lesson.
            for hour in range(start_hour, end_hour):
                self.pdf.cell(30, 10, f"{hour}:00", border=1, align='C')
                # Find lessons in this day that start during the current hour.
                lessons_this_hour = [lesson for lesson in lessons_by_day[day] if lesson.date.hour == hour]
                if lessons_this_hour:
                    # For demonstration, we'll list the lesson's start time (formatted) and price.
                    lesson_texts = []
                    for lesson in lessons_this_hour:
                        lesson_texts.append(lesson.to_dict()['date'])
                    cell_text = "\n".join(lesson_texts)
                else:
                    cell_text = "Wolne"  # Free
                # Use multi_cell for the lesson cell to handle potential multiple lines.
                self.pdf.multi_cell(0, 10, cell_text, border=1, align='C')

        # Save the PDF file in a folder named "lesson_plans"
        output_folder = "lesson_plans"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        file_name = f"lesson_plan_{date.today().strftime('%Y-%m-%d')}.pdf"
        file_path = os.path.join(output_folder, file_name)
        self.pdf.output(file_path)
        print(f"Lesson plan PDF saved as {file_path}")
        return file_path

