from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, ValidationError, Email
from .models import User

class RegistrationForm(FlaskForm):
  username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
    render_kw={
      "placeholder": "Username",
      "class": "form-control",
      "id": "InputText1",
      })
  email = EmailField(validators=[InputRequired(), Email()],
    render_kw={
      "placeholder": "Email Address",
      "class": "form-control",
      "aria-describedby": "emailHelp",
      "id": "InputEmail1",
      })
  password = PasswordField(validators=[InputRequired(), Length(min=8, max=22)],
    render_kw={
      "placeholder": "Password",
      "class": "form-control",
      "id": "InputPassword1",
      })
  submit = SubmitField("Sign Up", render_kw={"class": "btn btn-success"})

  def validate_email(self, email):
    existing_user_email = User.query.filter_by(
      email=email.data).first()
    if(existing_user_email):
      raise ValidationError("This email already exists. Please use another one.")

class LoginForm(FlaskForm):
  email = EmailField(validators=[InputRequired(), Email()],
    render_kw={
      "placeholder": "Email Address",
      "class": "form-control",
      "aria-describedby": "emailHelp",
      "id": "InputEmail1",
      })
  password = PasswordField(validators=[InputRequired(), Length(min=8, max=22)],
    render_kw={
      "placeholder": "Password",
      "class": "form-control",
      "id": "InputPassword1",
      })
  rememberme = BooleanField()
  submit = SubmitField("Sign In", render_kw={"class": "btn btn-primary"})