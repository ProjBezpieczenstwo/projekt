from flask import jsonify

from helper import get_object_or_404
from models import Teacher, Review, Lesson, db


class ReviewService:
    @staticmethod
    def get_reviews():
        reviews = Review.query.all()
        reviews_list = [r.to_dict() for r in reviews]
        return jsonify(reviews=reviews_list), 200

    @staticmethod
    def get_reviews_by_teacher_id(teacher_id):
        teacher = get_object_or_404(Teacher, teacher_id)
        if not isinstance(teacher, Teacher):
            return teacher

        reviews = Review.query.filter_by(teacher_id=teacher_id).all()
        reviews_list = [r.to_dict() for r in reviews]

        return jsonify(reviews=reviews_list), 200

    @staticmethod
    def add_review(user, data):
        lesson_id = data.get('lesson_id')
        rating = data.get('rating')
        rating = int(rating)
        comment = data.get('comment')
        lessons = get_object_or_404(Lesson, lesson_id)
        if not isinstance(lessons, Lesson):
            return teacher

        if not rating:
            return abort(400, description='Rating must be provided')

        if rating < 0 or rating > 5:
            return abort(400, description='Rating must be between values 0 and 5')

        if not comment:
            comment = ""
        teacher_id = lessons.teacher_id
        lessons.is_reviewed = True
        new_review = Review(teacher_id=teacher_id, student_id=user.id, rating=rating, comment=comment)
        db.session.add(new_review)
        db.session.add(lessons)
        db.session.commit()

        return jsonify({"message": "Review created successfully."}), 200

    @staticmethod
    def delete_review(user, teacher_id):
        review = Review.query.filter_by(teacher_id=teacher_id, student_id=user.id).first()

        if not review:
            return abort(400, description='Review does not exist')

        db.session.delete(review)
        db.session.commit()

        return jsonify({"message": "Review deleted successfuly"}), 200
