from fpdf import FPDF
from datetime import date
import os


class PDFInvoiceGenerator:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)

    def create_calendar(self, weekdays_with_hours, lessons):
        self.pdf.add_page()
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, "Kalendarz Zajęć", ln=True, align='C')

        self.pdf.ln(10)
        self.pdf.set_font('Arial', '', 12)
        self.pdf.multi_cell(0, 10, "Poniżej znajduje się harmonogram zajęć od dzisiaj.", align='C')

        # Dodawanie szczegółów kalendarza
        self.pdf.ln(10)
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(50, 10, "Dzień tygodnia", border=1)
        self.pdf.cell(50, 10, "Godzina od", border=1)
        self.pdf.cell(50, 10, "Godzina do", border=1, ln=True)

        self.pdf.set_font('Arial', '', 12)
        for day, start, end in weekdays_with_hours:
            self.pdf.cell(50, 10, day, border=1)
            self.pdf.cell(50, 10, str(start), border=1)
            self.pdf.cell(50, 10, str(end), border=1, ln=True)

        # Zapisanie PDF
        output_folder = "static_calendars"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        file_name = f"calendar_{date.today()}.pdf"
        file_path = os.path.join(output_folder, file_name)
        self.pdf.output(file_path)

        print(f"Calendar PDF saved as {file_name}")
        return file_path