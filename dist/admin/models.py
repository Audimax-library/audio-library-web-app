from admin import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  userlevel = db.Column(db.Integer, db.ForeignKey('userlevel.id'),nullable=False, default=0)
  username = db.Column(db.String(200), nullable=False)
  email = db.Column(db.String(80), nullable=False, unique=True)
  password = db.Column(db.String(64), nullable=False)

  def __repr__(self):
    return f'{self.email}'

class Userlevel(db.Model):
  id = db.Column(db.Integer, autoincrement=False, primary_key=True)
  title = db.Column(db.String(20), nullable=False)
  created_on = db.Column(db.DateTime, server_default=db.func.now())

  def __repr__(self):
    return f'{self.id}-{self.title}'