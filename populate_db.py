import random
from datetime import datetime, time

from faker import Faker
from models import Teacher, Student, Lesson, Review, Invoice, LessonReport, Calendar, Subject, DifficultyLevel, db
from server import app

fake = Faker()


def populate_subjects():
    with app.app_context():
        if not Subject.query.filter_by(id=1).first():
            subjects = [
                Subject(id=1, name="Maths"),
                Subject(id=2, name="Physics"),
                Subject(id=3, name="Biology"),
                Subject(id=4, name="Chemistry"),
                Subject(id=5, name="Geography"),
                Subject(id=6, name="Science"),
                Subject(id=7, name="IT"),
                Subject(id=8, name="English"),
                Subject(id=9, name="Polish"),
                Subject(id=10, name="Spanish"),
                Subject(id=11, name="French"),
                Subject(id=12, name="German"),
                Subject(id=13, name="Italian"),
            ]
            db.session.add_all(subjects)
            db.session.commit()
            print(f"Dodano przedmioty do bazy danych.")


def populate_difficulty_levels():
    with app.app_context():
        if not DifficultyLevel.query.filter_by(id=1).first():
            difficulty_levels = [
                DifficultyLevel(id=1, name="Primary School"),
                DifficultyLevel(id=2, name="Lower Secondary School"),
                DifficultyLevel(id=3, name="Higher Secondary School"),
                DifficultyLevel(id=4, name="Bachelor's"),
                DifficultyLevel(id=5, name="Master's"),
            ]


            db.session.add_all(difficulty_levels)
            db.session.commit()

            print(f"Dodano poziomy nauczania do bazy danych.")


def populate_teachers(num):
    with app.app_context():
        for _ in range(num):
            teacher = Teacher(
                name=fake.name(),
                email=fake.email(),
                subject_ids=random.sample(range(1, 14), random.randint(1, 3)),
                difficulty_level_ids=random.sample(range(1, 6), random.randint(1, 3)),
                hourly_rate=random.randint(50, 150),
                role="teacher"
            )
            teacher.set_password("pass")
            db.session.add(teacher)
        db.session.commit()
        print(f"{num} nauczycieli dodano do bazy danych.")


def populate_students(num):
    with app.app_context():
        for _ in range(num):
            student = Student(
                name=fake.name(),
                email=fake.email(),
                role="student"
            )
            student.set_password("pass")
            db.session.add(student)
        db.session.commit()
        print(f"{num} studentów dodano do bazy danych.")


def populate_lessons(num):
    with app.app_context():
        teachers = Teacher.query.all()
        students = Student.query.all()

        if not teachers or not students:
            print("Brak nauczycieli lub studentów w bazie danych.")
            return

        for _ in range(num):
            teacher = random.choice(teachers)
            student = random.choice(students)
            date = fake.date_time_this_year()
            subject_id = random.choice(teacher.subject_ids[1:-1].split(","))
            difficulty_level_id = random.choice(teacher.difficulty_level_ids[1:-1].split(","))

            lesson = Lesson(
                teacher_id=teacher.id,
                student_id=student.id,
                date=date,
                subject_id=subject_id,
                difficulty_level_id=difficulty_level_id,
                status="scheduled",
                price=teacher.hourly_rate
            )
            db.session.add(lesson)
        db.session.commit()
        print(f"{num} lekcji dodano do bazy danych.")


def populate_reviews(num):
    with app.app_context():
        lessons = Lesson.query.all()

        if not lessons:
            print("Brak lekcji w bazie danych.")
            return

        for lesson in lessons:
            if lesson.teacher_id and lesson.student_id:
                review = Review(
                    teacher_id=lesson.teacher_id,
                    student_id=lesson.student_id,
                    rating=random.randint(1, 5),
                    comment=fake.text()
                )
                db.session.add(review)
        db.session.commit()
        print(f"{num} recenzji dodano do bazy danych.")


def populate_invoices(num):
    with app.app_context():
        lessons = Lesson.query.filter_by(status="scheduled").all()

        if not lessons:
            print("Brak lekcji do wystawienia faktur.")
            return

        for _ in range(min(num, len(lessons))):
            lesson = random.choice(lessons)

            invoice = Invoice(
                lesson_id=lesson.id,
                email_sent=True
            )
            db.session.add(invoice)
        db.session.commit()
        print(f"{num} faktur dodano do bazy danych.")


def populate_reports(num):
    with app.app_context():
        lessons = Lesson.query.all()

        if not lessons:
            print("Brak lekcji w bazie danych.")
            return

        for lesson in lessons:
            report = LessonReport(
                lesson_id=lesson.id,
                teacher_id=lesson.teacher_id,
                homework=fake.word(),
                progress_rating=random.randint(1, 5),
                comment=fake.text(),
                student_id=lesson.student_id
            )
            db.session.add(report)
        db.session.commit()
        print(f"{num} raportów dodano do bazy danych.")


def populate_calendars(num):
    with app.app_context():
        teachers = Teacher.query.all()

        if not teachers:
            print("Brak nauczycieli w bazie danych.")
            return

        for teacher in teachers:
            available_from = time(random.randint(8, 10), 0, 0)  # Dostępne od 8:00-10:00
            available_until = time(random.randint(17, 20), 0, 0)  # Dostępne do 17:00-20:00
            working_days = random.sample(range(1, 8), random.randint(3, 5))  # 3-5 dni roboczych

            calendar = Calendar(
                teacher_id=teacher.id,
                available_from=available_from,
                available_until=available_until,
                working_days=working_days
            )
            db.session.add(calendar)
        db.session.commit()
        print(f"{num} kalendarzy dodano do bazy danych.")


if __name__ == "__main__":
    num_records = 10
    populate_difficulty_levels()
    populate_subjects()
    populate_teachers(num_records)
    populate_students(num_records)
    populate_lessons(num_records)
    populate_reviews(num_records)
    # populate_invoices(num_records)
    populate_reports(num_records)
    populate_calendars(num_records)


