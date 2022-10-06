#from webapp.extensions import db
from flask_sqlalchemy import SQLAlchemy
from fastapi_utils.guid_type import GUID
from uuid import uuid4
from webapp import db

class Release(db.Model):
  id = db.Column(GUID(), primary_key=True, default=uuid4)
  title = db.Column(db.String(80), nullable=False, unique=True)
  artist = db.Column(db.String(80), nullable=False, unique=False)
  cover_img = db.Column(db.String(80), nullable=False, unique=False)
  description = db.Column(db.String(100), unique=False)

  def __repr__(self):
    return f'{self.title}'