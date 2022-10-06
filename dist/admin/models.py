#from webapp.extensions import db
from flask_sqlalchemy import SQLAlchemy
from fastapi_utils.guid_type import GUID
from uuid import uuid4
from admin import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
  id = db.Column(GUID(), primary_key=True, default=uuid4)
  username = db.Column(db.String(20), nullable=False)
  email = db.Column(db.String(80), nullable=False, unique=True)
  password = db.Column(db.String(64), nullable=False)

  def __repr__(self):
    return f'{self.email}'


