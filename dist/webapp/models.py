from webapp import db
from admin.models import User, Userlevel
import datetime

book_genres = db.Table("book_genres",
  db.Column("book_id", db.Integer, db.ForeignKey("book.id", onupdate='CASCADE', ondelete='CASCADE'), primary_key=True),
  db.Column("genre_id", db.Integer, db.ForeignKey("genre.id", onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
)


class Book(db.Model):
  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  title = db.Column(db.String(100), nullable=False, unique=True)
  alt_title = db.Column(db.String(200), nullable=True, unique=False)
  cover_img = db.Column(db.String(100), nullable=False, unique=False, server_default="default_cover.jpg")
  synopsis = db.Column(db.String(1000), nullable=True, unique=False)
  status = db.Column(db.String(50), nullable=False, unique=False)
  language = db.Column(db.String(50), nullable=False, unique=False)
  views = db.Column(db.Integer, nullable=False, default=0)
  created = db.Column(db.DateTime, server_default=db.func.now())
  updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
  author_name = db.Column(db.String(200), nullable=False, unique=False)
  is_approved = db.Column(db.Boolean, unique=False, default=0)
  draft_user_email = db.Column(db.String(200), db.ForeignKey(User.email, onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
  chapters = db.relationship('Chapter', back_populates="book_obj")
  genres = db.relationship("Genre", secondary=book_genres, back_populates="books")
  users = db.relationship(User, backref="book")

  def __repr__(self):
    return f'{self.title}'


class Genre(db.Model):
  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  title = db.Column(db.String(100), nullable=False, unique=True)
  created = db.Column(db.DateTime, server_default=db.func.now())
  updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
  books = db.relationship("Book", secondary=book_genres, back_populates="genres")

  def __repr__(self):
    return f'{self.id}-{self.title}'


class Chapter(db.Model):
  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  order = db.Column(db.Integer, nullable=False, unique=False)
  display_number = db.Column(db.String(10), nullable=False, unique=False)
  audio_url = db.Column(db.String(100), nullable=False, unique=False, server_default="sample.mp3")
  is_convert = db.Column(db.Boolean, unique=False, default=0)
  read_text_url = db.Column(db.String(100), nullable=True, unique=False)
  views = db.Column(db.Integer, nullable=False, default=0)
  created = db.Column(db.DateTime, server_default=db.func.now())
  updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
  uploaded_by = db.Column(db.String(200), db.ForeignKey(User.email, onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
  book_id = db.Column(db.Integer, db.ForeignKey('book.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
  users = db.relationship(User, backref="chapter")

  book_obj = db.relationship("Book", back_populates="chapters")

  def __repr__(self):
    return f'Chapter-{self.display_number}'

  @property
  def elapsed_time(self):
    current_time = datetime.datetime.now()
    difference = current_time - self.created
    total_seconds = difference.total_seconds()
    if total_seconds > 365*24*60*60: #years
      return f"{int(divmod(total_seconds, 365*24*60*60)[0])} years ago..."
    elif total_seconds > 30*24*60*60: #months
      return f"{int(divmod(total_seconds, 30*24*60*60)[0])} months ago..."
    elif total_seconds > 7*24*60*60: #weeks
      return f"{int(divmod(total_seconds, 7*24*60*60)[0])} weeks ago..."
    elif total_seconds > 24*60*60: #days
      return f"{int(divmod(total_seconds, 24*60*60)[0])} days ago..."
    elif total_seconds > 60*60: #hours
      return f"{int(divmod(total_seconds, 60*60)[0])} hours ago..."
    elif total_seconds > 60: #minutes
      return f"{int(divmod(total_seconds, 60)[0])} minutes ago..."
    elif total_seconds > 5: #seconds
      return f"{int(total_seconds)} seconds ago..."
    else:
      return "Right now..."


class Library(db.Model):
  book_id = db.Column(db.Integer, db.ForeignKey('book.id', onupdate='CASCADE', ondelete='CASCADE'),nullable=False, primary_key=True)
  user_email = db.Column(db.String(200), db.ForeignKey(User.email, onupdate='CASCADE', ondelete='CASCADE'),nullable=False, primary_key=True)

  def __repr__(self):
    return f'Library-{self.book_id}-{self.user_email}'

class Rating(db.Model):
  book_id = db.Column(db.Integer, db.ForeignKey('book.id', onupdate='CASCADE', ondelete='CASCADE'),nullable=False, primary_key=True)
  user_email = db.Column(db.String(200), db.ForeignKey(User.email, onupdate='CASCADE', ondelete='CASCADE'),nullable=False, primary_key=True)
  rate_score = db.Column(db.Integer, nullable=False)
  created_date = db.Column(db.DateTime, server_default=db.func.now())
  updated = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

  def __repr__(self):
    return f'Rating-{self.book_id}-{self.user_email}-score{self.rate_score}'

class ReportBook(db.Model):
  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  user_email = db.Column(db.String(200), db.ForeignKey(User.email, onupdate='CASCADE', ondelete='CASCADE'),nullable=False)
  title = db.Column(db.String(100), nullable=False, unique=False)
  subject = db.Column(db.String(1000), nullable=True, unique=False)
  is_read = db.Column(db.Boolean, unique=False, default=0)
  created_date = db.Column(db.DateTime, server_default=db.func.now())

  def __repr__(self):
    return f'Report-{self.id}-{self.title}-{self.user_email}'

# newsletter model
class NewsLetterSubscription(db.Model):
  subscription_id = db.Column(db.Integer, autoincrement=True, nullable=False, unique=True, primary_key=True)
  email = db.Column(db.String(80), nullable=False, unique=True, primary_key=True)
  created_date = db.Column(db.DateTime, server_default=db.func.now())

  def __repr__(self):
    return f'MailID-{self.subscription_id}'

class ListenHistory(db.Model):
  user_email = db.Column(db.String(200), db.ForeignKey(User.email, onupdate='CASCADE', ondelete='CASCADE'), nullable=False, primary_key=True)
  chapter_id = db.Column(db.Integer, db.ForeignKey(Chapter.id, onupdate='CASCADE', ondelete='CASCADE'), nullable=False, primary_key=True)
  first_heard_on = db.Column(db.DateTime, server_default=db.func.now())
  last_heard_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

  def __repr__(self):
    return f'History-{self.user_email}-{self.chapter_id}-{self.last_heard_on}'


# db.create_all()
# skeleton data

""" memberlvl = Userlevel(id=0, title="member")
adminlvl = Userlevel(id=1, title="admin")
db.session.add(memberlvl)
db.session.add(adminlvl)
objects = [
    Genre(title="Action and Adventure"),
    Genre(title="Classics"),
    Genre(title="Graphic Novel"),
    Genre(title="Detective and Mystery"),
    Genre(title="Fantasy"),
    Genre(title="Horror"),
    Genre(title="Literary Fiction"),
    Genre(title="Romance"),
    Genre(title="Women's Fiction"),
    Genre(title="Biographies and Autobiographies"),
    Genre(title="Science Fiction (Sci-Fi)"),
    Genre(title="Short Stories"),
    Genre(title="Suspense and Thrillers"),
    Genre(title="Historical Fiction"),
    Genre(title="Cookbooks"),
    Genre(title="Essays"),
    Genre(title="History"),
    Genre(title="Memoir"),
    Genre(title="Poetry"),
    Genre(title="Self-Help"),
    Genre(title="True Crime")
]
db.session.bulk_save_objects(objects)
db.session.commit() """
