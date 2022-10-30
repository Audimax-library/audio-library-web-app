from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db_user = 'dulan'
db_pswd = 'good'
db_host = 'localhost'
db_name = 'llamaloops_db'


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{db_user}:{db_pswd}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from admin_model import User, Userlevel

book_genre = db.Table('book_genre',
  db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
  db.Column('genre_id', db.Integer, db.ForeignKey('genre.id')),
)

class Book(db.Model):
  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  title = db.Column(db.String(100), nullable=False, unique=True)
  alt_title = db.Column(db.String(200), nullable=True, unique=False)
  cover_img = db.Column(db.String(100), nullable=False, unique=False, server_default="default_cover.jpg")
  synopsis = db.Column(db.String(1000), nullable=True, unique=False)
  type = db.Column(db.String(50), nullable=False, unique=False)
  status = db.Column(db.String(50), nullable=False, unique=False)
  language = db.Column(db.String(50), nullable=False, unique=False)
  views = db.Column(db.Integer, nullable=False, default=0)
  created = db.Column(db.DateTime, server_default=db.func.now())
  updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
  author_id = db.Column(db.Integer, db.ForeignKey('author.id'),nullable=False)
  chapters = db.relationship('Chapter', backref="book")
  genre_tags = db.relationship('Genre', secondary=book_genre, backref="tagged_books")

  def __repr__(self):
    return f'{self.title}'

class Chapter(db.Model):
  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  order = db.Column(db.Integer, nullable=False, unique=True)
  display_number = db.Column(db.String(10), nullable=False, unique=False)
  audio_url = db.Column(db.String(100), nullable=False, unique=False, server_default="sample.mp3")
  read_text_url = db.Column(db.String(100), nullable=True, unique=False)
  views = db.Column(db.Integer, nullable=False, default=0)
  created = db.Column(db.DateTime, server_default=db.func.now())
  updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
  book_id = db.Column(db.Integer, db.ForeignKey('book.id'),nullable=False)

  def __repr__(self):
    return f'Chapter-{self.display_number}'

class Genre(db.Model):
  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  title = db.Column(db.String(50), nullable=False, unique=True)
  created = db.Column(db.DateTime, server_default=db.func.now())
  updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

  def __repr__(self):
    return f'{self.title}'

class Author(db.Model):
  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  name = db.Column(db.String(200), nullable=False, unique=True)
  created = db.Column(db.DateTime, server_default=db.func.now())
  updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
  books = db.relationship('Book', backref="author")

  def __repr__(self):
    return f'{self.name}'

class Rating(db.Model):
  rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  score = db.Column(db.Integer, nullable=False)

  users = db.relationship("User", backref=db.backref("rating", order_by=rating_id))
  books = db.relationship("Book", backref=db.backref("rating", order_by=rating_id))
  
  def __repr__(self):
    return f'Movie{self.book_id}-User{self.user_id}-score{self.score}'


db.create_all()

#skeleton data

memberlvl = Userlevel(id=0, title="member")
adminlvl = Userlevel(id=1, title="admin")
db.session.add(memberlvl)
db.session.add(adminlvl)
db.session.commit()