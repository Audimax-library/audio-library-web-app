#from webapp.extensions import db
from flask_sqlalchemy import SQLAlchemy
from fastapi_utils.guid_type import GUID
from uuid import uuid4
from admin import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
  id = db.Column(GUID(), primary_key=True, default=uuid4)
  userlevel = db.Column(db.Integer, db.ForeignKey('userlevel.id'),nullable=False, default=0)
  username = db.Column(db.String(200), nullable=False)
  email = db.Column(db.String(80), nullable=False, unique=True)
  password = db.Column(db.String(64), nullable=False)

  def __repr__(self):
    return f'{self.email}'

class Userlevel(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(20), nullable=False)
  created_on = db.Column(db.DateTime, server_default=db.func.now())
