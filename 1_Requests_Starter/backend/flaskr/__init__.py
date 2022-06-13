import os
from venv import create
from flask import Flask, request, abort, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random
import json
from models import setup_db, Book, db

BOOKS_PER_SHELF = 8

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there.
#     If you do not update the endpoints, the lab will not work - of no fault of your API code!
#   - Make sure for each route that you're thinking through when to abort and with which kind of error
#   - If you change any of the response body keys, make sure you update the frontend to correspond.


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
    @app.route('/')
    def index():
        return redirect(url_for('get_all_books'))
    # @TODO: Write a route that retrivies all books, paginated.
    #         You can use the constant above to paginate by eight books.
    #         If you decide to change the number of books per page,
    #         update the frontend to handle additional books in the styling and pagination
    #         Response body keys: 'success', 'books' and 'total_books'
    # TEST: When completed, the webpage will display books including title, author, and rating shown as stars
    @app.route('/books', methods=['GET', 'POST'])
    def get_all_books():
        books = Book.query.order_by('id').all()
        curr_page = request.args.get('page', 1, type=int)
        start = (curr_page - 1) * BOOKS_PER_SHELF
        end = (start + BOOKS_PER_SHELF if start + BOOKS_PER_SHELF <= len(books) else None)

        formatted_books = [book.format() for book in books]
        return jsonify({
            'status_code': 200,
            'books': formatted_books[start:end],
            'total_books': len(books)
        })
    # @TODO: Write a route that will update a single book's rating.
    #         It should only be able to update the rating, not the entire representation
    #         and should follow API design principles regarding method and route.
    #         Response body keys: 'success'
    # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh
    @app.route('/book/update_rating/<int:book_id>', methods=['PATCH'])
    def update_rating(book_id):
        book = Book.query.get_or_404(book_id)
        book.rating = request.args.get('rating', 0, type=int)
        try:
            book.update()
        except Exception as e:
            db.session.rollback()
            print(e)
        finally:
            db.session.close()
        return jsonify({
            'status': 200
        })

    # @TODO: Write a route that will delete a single book.
    #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
    #        Response body keys: 'success', 'books' and 'total_books'
    @app.route('/books/delete/<int:book_id>', methods=['DELETE'])
    def delete_book(book_id):
        book = Book.query.get_or_404(book_id)
        try:
            book.delete()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify({
            'status': 200
        })
    # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.

    # @TODO: Write a route that create a new book.
    #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
    # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books.
    #       Your new book should show up immediately after you submit it at the end of the page.
    @app.route('/books/create_book', methods=['POST'])
    def create_book():
        data = json.loads(request.data.decode('utf-8'))
        title = data['title']
        rating = data['rating']
        author= data['author']

        new_book = Book(
            title=title,
            author=author,
            rating=rating
        )
        try:
            new_book.insert()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify({
            'status': 200,
            'rating': rating,
            'author': author,
            'title': title
        })

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()