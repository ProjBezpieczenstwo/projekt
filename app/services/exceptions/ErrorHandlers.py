from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({
            'error': {
                'type': e.name,
                'message': e.description,
                'code': e.code
            }
        }), e.code

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        return jsonify({
            'error': {
                'type': 'Internal Server Error',
                'message': str(e),
                'code': 500
            }
        }), 500
