import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from data_models import Author, Book, db

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database configuration
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(base_dir, '../data', 'library.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)


@app.route("/", methods=["GET"])
def home():
    keyword = request.args.get("keyword", "").strip()
    sort_by = request.args.get("sort_by", "title")

    # Base query
    query = Book.query.join(Author)

    # Apply search filter if keyword exists
    if keyword:
        query = query.filter(
            db.or_(
                Book.title.ilike(f"%{keyword}%"),
                Author.name.ilike(f"%{keyword}%")
            )
        )

    # Fetch books with optional sorting
    if sort_by == "title":
        query = query.order_by(Book.title)
    elif sort_by == "author_name":
        query = query.order_by(Author.name)

    books = query.all()

    return render_template("home.html", books=books)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        try:
            # Retrieve form data
            name = request.form["name"]
            birth_date = datetime.strptime(request.form["birthdate"], "%Y-%m-%d").date()
            date_of_death = (
                datetime.strptime(request.form["date_of_death"], "%Y-%m-%d").date()
                if request.form["date_of_death"]
                else None
            )

            # Create and add author
            new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
            db.session.add(new_author)
            db.session.commit()

            return render_template("add_author.html", message="Author added successfully!")
        except Exception as e:
            db.session.rollback()
            return render_template("add_author.html", error=f"An error occurred: {e}")
    return render_template("add_author.html")


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"]
        isbn = request.form["isbn"]
        publication_year = request.form["publication_year"]
        author_id = request.form["author_id"]

        # Create and add book
        new_book = Book(title=title, isbn=isbn, publication_year=publication_year, author_id=author_id)
        db.session.add(new_book)
        db.session.commit()

        flash(f"Book '{title}' added successfully!", "success")
        return redirect("/add_book")

    authors = Author.query.all()
    return render_template("add_book.html", authors=authors)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)

    # Check if the author has other books
    author = book.author
    db.session.delete(book)
    db.session.commit()

    # If the author has no other books, delete the author
    if not author.books:
        db.session.delete(author)
        db.session.commit()

    flash(f"Book '{book.title}' deleted successfully!", "success")
    return redirect(url_for("home"))


@app.route("/book/<int:book_id>")
def book_detail(book_id):
    """Render the detail page for a specific book."""
    book = Book.query.get_or_404(book_id)
    return render_template("book_detail.html", book=book)


@app.route("/author/<int:author_id>")
def author_detail(author_id):
    """Render the detail page for a specific author."""
    author = Author.query.get_or_404(author_id)
    return render_template("author_detail.html", author=author)


@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)

    # Delete the author and cascade delete their books
    db.session.delete(author)
    db.session.commit()

    # Redirect to home with success message
    flash(f"Author '{author.name}' and all associated books have been deleted.", 'success')
    return redirect(url_for('home'))


# if __name__ == '__main__':
#     app.run(debug=True)
#     with app.app_context():
#         db.create_all()
#         print("Tables created successfully!")

# with app.app_context():
#     db.create_all()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database and Tables initialized successfully")
        # Seed authors
        # authors = [
        #     {"name": "J.K. Rowling", "birth_date": datetime.strptime("1965-07-31", "%Y-%m-%d").date(),
        #      "date_of_death": None},
        #     {"name": "George Orwell", "birth_date": datetime.strptime("1903-06-25", "%Y-%m-%d").date(),
        #      "date_of_death": datetime.strptime("1950-01-21", "%Y-%m-%d").date()},
        #     {"name": "Jane Austen", "birth_date": datetime.strptime("1775-12-16", "%Y-%m-%d").date(),
        #      "date_of_death": datetime.strptime("1817-07-18", "%Y-%m-%d").date()},
        #     {"name": "Mark Twain", "birth_date": datetime.strptime("1835-11-30", "%Y-%m-%d").date(),
        #      "date_of_death": datetime.strptime("1910-04-21", "%Y-%m-%d").date()},
        #     {"name": "Harper Lee", "birth_date": datetime.strptime("1926-04-28", "%Y-%m-%d").date(),
        #      "date_of_death": datetime.strptime("2016-02-19", "%Y-%m-%d").date()},
        # ]
        #
        # for author_data in authors:
        #     author = Author(
        #         name=author_data["name"],
        #         birth_date = author_data["birth_date"],
        #         date_of_death = author_data["date_of_death"],
        #     )
        #     db.session.add(author)
        #
        # # Commit authors to the database
        # db.session.commit()

        # Seed books
        # books = [
        #     {"isbn": "9780747532743", "title": "Harry Potter and the Philosopher's Stone", "publication_year": 1997,
        #      "author_id": 1},
        #     {"isbn": "9780451524935", "title": "1984", "publication_year": 1949, "author_id": 2},
        #     {"isbn": "9780141439518", "title": "Pride and Prejudice", "publication_year": 1813, "author_id": 3},
        #     {"isbn": "9780143107323", "title": "The Adventures of Huckleberry Finn", "publication_year": 1884,
        #      "author_id": 4},
        #     {"isbn": "9780060935467", "title": "To Kill a Mockingbird", "publication_year": 1960, "author_id": 5},
        # ]
        #
        # for book_data in books:
        #     book = Book(
        #         isbn=book_data["isbn"],
        #         title = book_data["title"],
        #         publication_year = book_data["publication_year"],
        #         author_id = book_data["author_id"],
        #     )
        #     db.session.add(book)
        #
        # # commit books to the database
        # db.session.commit()
        #
        # print("Books added successfully!")

    app.run(debug=True)
