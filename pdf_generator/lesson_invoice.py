from datetime import datetime

class LessonInvoice:
    def __init__(
        self,
        invoice_id: int,
        lesson_id: int,
        student_name: str,
        student_email: str,
        teacher_name: str,
        teacher_email: str,
        subject: str,
        lesson_date: datetime,
        price: float,
        vat_rate: float,
        issue_date: datetime
    ):
        self.invoice_id = invoice_id
        self.lesson_id = lesson_id
        self.student_name = student_name
        self.student_email = student_email
        self.teacher_name = teacher_name
        self.teacher_email = teacher_email
        self.subject = subject
        self.lesson_date = lesson_date
        self.price = price
        self.vat_rate = vat_rate
        self.issue_date = issue_date

    def to_dict(self):
        return {
            "invoice_id": self.invoice_id,
            "lesson_id": self.lesson_id,
            "student_name": self.student_name,
            "student_email": self.student_email,
            "teacher_name": self.teacher_name,
            "teacher_email": self.teacher_email,
            "subject": self.subject,
            "lesson_date": self.lesson_date.isoformat(),
            "price": self.price,
            "vat_rate": self.vat_rate,
            "issue_date": self.issue_date.isoformat()
        }
