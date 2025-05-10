from flask import abort
from flask_jwt_extended import get_jwt_identity

from models import BaseUser


def get_object_or_404(model, object_id, type_cast=int):
    if object_id is None:
        abort(400, description=f'{model.__name__} ID is not provided')

    try:
        parsed_id = type_cast(object_id)
    except (ValueError, TypeError):
        abort(400, description=f'{object_id} must be a valid {type_cast.__name__}')

    obj = model.query.filter_by(id=parsed_id).first()
    if obj is None:
        abort(404, description=f'{model.__name__} not found')

    return obj


def get_user_by_jwt():
    user_id = get_jwt_identity()
    return BaseUser.query.filter_by(id=user_id).first()
