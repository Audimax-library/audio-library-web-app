from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField, TextAreaField
from wtforms.validators import InputRequired

class UploadFileForm(FlaskForm):
  title = StringField("title")
  artist = StringField("artist")
  file = FileField("file", validators=[InputRequired()])
  description = TextAreaField("description")
  submit = SubmitField("Upload File")