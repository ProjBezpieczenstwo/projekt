from fpdf import FPDF
import os

from pdf_generator.lesson_invoice import LessonInvoice


class PDFInvoiceGenerator:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)

    def create_invoice(self, lesson_invoice: LessonInvoice):
        self.pdf.add_page()
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, "Invoice", ln=True, align='C')

        # Adding introductory description
        self.pdf.ln(10)
        self.pdf.set_font('Arial', '', 12)
        self.pdf.multi_cell(0, 10, ("This invoice is for an English tutoring lesson. "
                                    "It contains details of the lesson and payment information."), align='C')

        # Adding invoice details
        self.pdf.set_font('Arial', '', 12)
        self.pdf.ln(10)
        self.pdf.cell(0, 10, f"Invoice ID: {lesson_invoice.invoice_id}", ln=True)
        self.pdf.cell(0, 10, f"Lesson ID: {lesson_invoice.lesson_id}", ln=True)
        self.pdf.cell(0, 10, f"Subject: {lesson_invoice.subject}", ln=True)
        self.pdf.cell(0, 10, f"Lesson Date: {lesson_invoice.lesson_date.strftime('%Y-%m-%d')}", ln=True)

        # Adding student information
        self.pdf.ln(10)
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 10, "Student Information:", ln=True)
        self.pdf.set_font('Arial', '', 12)
        self.pdf.cell(0, 10, f"Name: {lesson_invoice.student_name}", ln=True)
        self.pdf.cell(0, 10, f"Email: {lesson_invoice.student_email}", ln=True)

        # Adding teacher information
        self.pdf.ln(10)
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 10, "Teacher Information:", ln=True)
        self.pdf.set_font('Arial', '', 12)
        self.pdf.cell(0, 10, f"Name: {lesson_invoice.teacher_name}", ln=True)
        self.pdf.cell(0, 10, f"Email: {lesson_invoice.teacher_email}", ln=True)

        # Adding payment details
        self.pdf.ln(10)
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 10, "Payment Details:", ln=True)
        self.pdf.set_font('Arial', '', 12)
        self.pdf.cell(0, 10, f"Price (Gross): ${lesson_invoice.price:.2f}", ln=True)
        self.pdf.cell(0, 10, f"VAT Rate: {lesson_invoice.vat_rate}%", ln=True)
        self.pdf.cell(0, 10, f"Issue Date: {lesson_invoice.issue_date.strftime('%Y-%m-%d')}", ln=True)

        # Ensuring the output directory exists
        output_folder = "static_invoices"

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Saving the PDF
        file_name = f"invoice_{lesson_invoice.invoice_id}.pdf"
        file_path = os.path.join(output_folder, file_name)

        self.pdf.output(file_path)
        print(f"Invoice PDF saved as {file_name}")
