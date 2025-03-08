import sys
import os
import pytest
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_generator.lesson_invoice import LessonInvoice


def test_to_dict():
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

    assert lesson_invoice.to_dict() == {
        "invoice_id": 1,
        "lesson_id": 1,
        "student_name": "Test Student",
        "student_email": "student@example.com",
        "teacher_name": "Test Teacher",
        "teacher_email": "teacher@example.com",
        "subject": "English",
        "lesson_date": "2025-01-01T00:00:00",
        "price": 50,
        "vat_rate": 23,
        "issue_date": "2025-01-02T00:00:00",
    }

    assert lesson_invoice.invoice_id == 1
    assert lesson_invoice.lesson_id == 1
    assert lesson_invoice.subject == "English"
    assert lesson_invoice.lesson_date == datetime(2025, 1, 1)
    assert lesson_invoice.student_name == "Test Student"
    assert lesson_invoice.student_email == "student@example.com"
    assert lesson_invoice.teacher_name == "Test Teacher"
    assert lesson_invoice.teacher_email == "teacher@example.com"
    assert lesson_invoice.price == 50
    assert lesson_invoice.vat_rate == 23
    assert lesson_invoice.issue_date == datetime(2025, 1, 2)




