import sys
import os
import pytest
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_generator.pdf_generator import PDFInvoiceGenerator
from pdf_generator.lesson_invoice import LessonInvoice


def test_create_invoice():
    """Test that the PDF generator creates an invoice correctly."""
    lesson_invoice = LessonInvoice(
        invoice_id=1,
        lesson_id=1,
        subject="English",
        lesson_date=datetime(2025, 1, 1),
        student_name="Test Student",
        student_email="student@example.com",
        teacher_name="Test Teacher",
        teacher_email="teacher@example.com",
        price=50,
        vat_rate=23,
        issue_date=datetime(2025, 1, 2))

    pdf_generator = PDFInvoiceGenerator()

    pdf_generator.create_invoice(lesson_invoice)
