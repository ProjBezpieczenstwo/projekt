import io
from datetime import date, timedelta

from fpdf import FPDF


class PDFLessonPlanGenerator:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        # Add Unicode fonts
        self.pdf.add_font("DejaVu", "", "./font/DejaVuSans.ttf", uni=True)
        self.pdf.add_font("DejaVu", "B", "./font/DejaVuSans-Bold.ttf", uni=True)
        # Mapping of English weekday names to local names
        self.day_names = {
            "Monday": "Poniedziałek",
            "Tuesday": "Wtorek",
            "Wednesday": "Środa",
            "Thursday": "Czwartek",
            "Friday": "Piątek",
            "Saturday": "Sobota",
            "Sunday": "Niedziela"
        }

    def wrap_text(self, text, cell_width):
        """
        Splits a text string into lines that fit within cell_width.
        Honors any explicit newlines present in the text.
        """
        pdf = self.pdf
        if not text:
            return [""]
        lines = []
        # Split text on explicit newlines first.
        for part in text.split("\n"):
            words = part.split()
            if not words:
                lines.append("")
                continue
            current_line = words[0]
            for word in words[1:]:
                test_line = current_line + " " + word
                if pdf.get_string_width(test_line) <= cell_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)
        return lines

    def print_row(self, cells, widths, line_height=5, fill_colors=None, alignments=None, fonts=None):
        """
        Prints a table row, wrapping text in each cell.

        - The text for each cell is wrapped using wrap_text.
        - Each cell is padded so that every cell has the same number of lines.
        - The row is printed line by line horizontally.
        - If a fonts list is provided, for each cell the font is set before printing.
        - Background colors (if provided) and cell borders are drawn.
        """
        pdf = self.pdf
        y_start, x_start = pdf.get_y(), pdf.get_x()

        # Wrap each cell's text and determine maximum number of lines
        wrapped = []
        max_lines = 0
        for i, cell in enumerate(cells):
            lines = self.wrap_text(cell, widths[i])
            wrapped.append(lines)
            max_lines = max(max_lines, len(lines))
        # Pad each cell to ensure equal number of lines
        for i in range(len(wrapped)):
            if len(wrapped[i]) < max_lines:
                wrapped[i].extend([""] * (max_lines - len(wrapped[i])))
        row_height = max_lines * line_height

        # Draw fill backgrounds for each cell, if provided
        current_x = x_start
        for i in range(len(cells)):
            if fill_colors and i < len(fill_colors) and fill_colors[i]:
                pdf.set_fill_color(*fill_colors[i])
                pdf.rect(current_x, y_start, widths[i], row_height, style='F')
            current_x += widths[i]

        # Print text for each line across cells
        for _ in range(max_lines):
            current_x = x_start
            for i in range(len(cells)):
                # If font info is provided for this cell, set it
                if fonts and i < len(fonts) and fonts[i]:
                    pdf.set_font(fonts[i][0], fonts[i][1], fonts[i][2])
                else:
                    # Otherwise, font remains as previously set.
                    pass
                align = alignments[i] if (alignments and i < len(alignments)) else 'C'
                pdf.set_xy(current_x, pdf.get_y())
                pdf.cell(widths[i], line_height, wrapped[i].pop(0), border=0, align=align)
                current_x += widths[i]
            pdf.ln(line_height)

        # Draw cell borders
        current_x = x_start
        for i in range(len(cells)):
            pdf.rect(current_x, y_start, widths[i], row_height)
            current_x += widths[i]
        pdf.set_xy(x_start, y_start + row_height)

    def generate_pdf(self, weekdays_with_hours, lessons):
        """
        Generates a weekly lesson plan PDF.

        Arguments:
          weekdays_with_hours: dict mapping weekday names (e.g. "Monday")
                               to a tuple (start_hour, end_hour)
          lessons: list of Lesson objects.
        """
        # Group lessons by (date, hour)
        lessons_by_day_hour = {}
        for lesson in lessons:
            dt = lesson.date
            key = (dt.date(), dt.hour)
            lessons_by_day_hour.setdefault(key, []).append(lesson)

        today = date.today()
        # Start from the Monday of the current week
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=30)
        line_height = 5
        # Define column widths: first column for hour, then 7 columns for week days
        col_widths = [25] + [23] * 7

        current_date = start_date
        while current_date <= end_date:
            self.pdf.add_page()
            self.pdf.set_font("DejaVu", "B", 14)
            week_end = current_date + timedelta(days=6)
            header = f"Plan tygodniowy od {current_date.strftime('%Y-%m-%d')} do {week_end.strftime('%Y-%m-%d')}"
            self.pdf.cell(0, 10, header, ln=True, align='C')
            self.pdf.ln(5)

            # Prepare header row: "Godzina" and then day cells with automatic line breaks
            week_dates = [current_date + timedelta(days=i) for i in range(7)]
            header_cells = ["Godzina"]
            for d in week_dates:
                day_key = d.strftime("%A")
                # Insert a newline between day name and date
                day_label = f"{self.day_names.get(day_key, day_key)}\n({d.strftime('%d.%m')})"
                header_cells.append(day_label)
            self.pdf.set_font("DejaVu", "B", 7)
            self.print_row(header_cells, col_widths, line_height=line_height)

            for hour in range(6, 22):
                row_cells = [f"{hour}:00"]
                row_fill = [None]
                # Build cells for each day of the week.
                for d in week_dates:
                    key = (d, hour)
                    weekday = d.strftime("%A")
                    if key in lessons_by_day_hour:
                        lesson_infos = []
                        for lesson in lessons_by_day_hour[key]:
                            info = lesson.to_dict()
                            lesson_infos.append(f"{info['subject']}\n{info['difficulty_id']}\n{info['student_id']}")
                        cell_text = "\n".join(lesson_infos)
                        fill_color = (0, 255, 0)
                    elif weekday in weekdays_with_hours and weekdays_with_hours[weekday][0] <= hour < \
                            weekdays_with_hours[weekday][1]:
                        cell_text = ""
                        fill_color = (200, 200, 200)
                    else:
                        cell_text = ""
                        fill_color = (255, 255, 255)
                    row_cells.append(cell_text)
                    row_fill.append(fill_color)
                row_fonts = [("DejaVu", "", 10)] + [("DejaVu", "", 8)] * 7
                self.print_row(row_cells, col_widths, line_height=line_height, fill_colors=row_fill, fonts=row_fonts)
            current_date += timedelta(days=7)

        pdf_output = io.BytesIO(self.pdf.output(dest="S").encode("latin1"))
        return pdf_output
