from flask import current_app, jsonify


def register_error_handlers(app):

    @app.errorhandler(400)
    def handle_400(error):
        return jsonify(
            {
                "error": "bad request",
                "code": 400,
            }
        ), 400

    @app.errorhandler(401)
    def handle_401(error):
        return jsonify(
            {
                "error": "unauthorized",
                "code": 401,
            }
        ), 401

    @app.errorhandler(403)
    def handle_403(error):
        return jsonify(
            {
                "error": "forbidden",
                "code": 403,
            }
        ), 403

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify(
            {
                "error": "resource not found",
                "code": 404,
            }
        ), 404

    @app.errorhandler(405)
    def handle_405(error):
        return jsonify(
            {
                "error": "method not allowed",
                "code": 405,
            }
        ), 405

    @app.errorhandler(413)
    def handle_413(error):
        return jsonify(
            {
                "error": "request entity too large",
                "code": 413,
            }
        ), 413

    @app.errorhandler(500)
    def handle_500(error):
        # Log the actual exception internally.
        current_app.logger.exception("Unhandled server exception")

        # NEVER expose error details to the client.
        return jsonify(
            {
                "error": "internal server error",
                "code": 500,
            }
        ), 500
