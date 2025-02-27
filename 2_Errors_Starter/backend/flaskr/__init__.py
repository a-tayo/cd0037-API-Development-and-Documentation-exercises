from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random

from models import setup_db, Book, db

BOOKS_PER_SHELF = 10


def paginate_books(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF

    books = [book.format() for book in selection]
    current_books = books[start:end]

    return current_books


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    @app.route("/books")
    def retrieve_books():
        selection = Book.query.order_by(Book.id).all()
        current_books = paginate_books(request, selection)

        if len(current_books) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "books": current_books,
                "total_books": len(Book.query.all()),
            }
        )

    @app.route("/books/<int:book_id>", methods=["PATCH"])
    def update_book(book_id):

        body = request.get_json()

        try:
            book = Book.query.get_or_404(book_id)

            if "rating" in body:
                book.rating = int(body.get("rating"))

            book.update()

            return jsonify(
                {
                    "success": True,
                }
            )

        except:
            db.session.rollback()

    @app.route("/books/<int:book_id>", methods=["DELETE"])
    def delete_book(book_id):
        try:
            book = Book.query.get_or_404(book_id)

            book.delete()
            selection = Book.query.order_by(Book.id).all()
            current_books = paginate_books(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": book_id,
                    "books": current_books,
                    "total_books": len(Book.query.all()),
                }
            )

        except:
            db.session.rollback()
            abort(422)

    @app.route("/books", methods=["POST"])
    def create_book():
        body = request.get_json()

        new_title = body.get("title", None)
        new_author = body.get("author", None)
        new_rating = body.get("rating", None)

        try:
            book = Book(title=new_title, author=new_author, rating=new_rating)
            book.insert()

            selection = Book.query.order_by(Book.id).all()
            current_books = paginate_books(request, selection)

            return jsonify(
                {
                    "success": True,
                    "created": book.id,
                    "books": current_books,
                    "total_books": len(Book.query.all()),
                }
            )

        except:
            abort(422)

    # @TODO: Review the above code for route handlers.
    #        Pay special attention to the status codes used in the aborts since those are relevant for this task!

    # @TODO: Write error handler decorators to handle AT LEAST status codes 400, 404, and 422.
    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            'success': False,
            'status': 404,
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'status': 405,
            'message': 'method not allowed'
        }), 405

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad Request'
        }), 400

    @app.errorhandler(422)
    def uprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Your request can not be processed'
        }), 422

    # TEST: Practice writing curl requests. Write some requests that you know will error in expected ways.
    #       Make sure they are returning as expected. Do the same for other misformatted requests or requests missing data.
    #       If you find any error responses returning as HTML, write new error handlers for them.

    return app

if __name__ == '__main__':
    app = create_app()
    app.debug = True
    app.run()
