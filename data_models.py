from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'

    author_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    books = db.relationship('Book', back_populates='author', cascade="all, delete", lazy=True)

    def __repr__(self):
        return f"<Author(id={self.author_id}, name='{self.name}')>"

    def __str__(self):
        return f"{self.name}"


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id'), nullable=False)

    author = db.relationship('Author', back_populates='books', lazy=True)

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}')>"

    def __str__(self):
        return f"{self.title}, ISBN: {self.isbn}"




# with app.app_context():
#     db.create_all()
