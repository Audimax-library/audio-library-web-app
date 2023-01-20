from app import db
from flask_login import UserMixin


class Userlevel(db.Model):
  id = db.Column(db.Integer, autoincrement=False, primary_key=True)
  title = db.Column(db.String(20), nullable=False)
  created_on = db.Column(db.DateTime, server_default=db.func.now())

  def __repr__(self):
    return f'{self.id}-{self.title}'

class User(db.Model, UserMixin):
  id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  userlevel = db.Column(db.Integer, db.ForeignKey('userlevel.id', onupdate='CASCADE', ondelete='CASCADE'),nullable=False, default=0)
  username = db.Column(db.String(200), nullable=False)
  email = db.Column(db.String(200), nullable=False, unique=True)
  password = db.Column(db.String(64), nullable=False)
  is_banned = db.Column(db.Boolean, unique=False, default=0)
  created_on = db.Column(db.DateTime, server_default=db.func.now())

  level_obj = db.relationship(Userlevel, backref="user")

  def __repr__(self):
    return f'{self.email}'
