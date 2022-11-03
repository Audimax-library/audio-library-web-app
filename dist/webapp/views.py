#from urllib import request
from flask import Blueprint,render_template, redirect, session, url_for, request, make_response, jsonify, flash
from .forms import UploadFileForm
from werkzeug.utils import secure_filename
import os
from uuid import uuid4
from webapp import db
from flask_login import login_required, login_user, logout_user, current_user
from admin import db, login_manager, oauth, discord, bcrypt
from admin.forms import LoginForm, RegistrationForm
from admin.models import User
import datetime
from sqlalchemy.exc import IntegrityError

webapp = Blueprint('webapp', __name__, static_folder="static", static_url_path='/webapp/static' , template_folder='templates')
UPLOAD_FOLDER = "static/uploads/"
login_manager.login_view = "webapp.login_page"

def make_unique(string):
    ident = uuid4().__str__()
    return f"{ident}-{string}"

@webapp.route("/", methods=['GET', 'POST'])
@webapp.route("/home/", methods=['GET', 'POST'])
def home_page():
    context = {}
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
        #user = User.query.filter_by(email=str(current_user)).first()
        context['user_name'] = current_user.username
    return render_template('home.html', context=context)

@webapp.route("/titles/", methods=['GET', 'POST'])
def titles_page():
    query = request.args.get('q')
    return f'<h1>{query}</h1>';

@webapp.route("/book/<id>", methods=['GET', 'POST'])
def book_page(id):
    context = {'id': id}
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
    return render_template('book.html', context=context)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@webapp.route("/login/", methods=['GET', 'POST'])
def login_page():
    if session.get('profile'):
        user_detail = session['profile']
        #print(user_detail['name'])
    if current_user.is_authenticated:
        return redirect(url_for('webapp.home_page'))

    form = LoginForm()
    if request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()
        #print(request.form.getlist('rememberme'))
        if(user):
            if(bcrypt.check_password_hash(user.password, form.password.data)):
                if(len(request.form.getlist('rememberme')) > 0):
                    login_user(user, remember=True, duration=datetime.timedelta(days=30))
                else:
                    login_user(user)
                flash('Login Successful.', 'success')
                return redirect(url_for('webapp.home_page'))
            else:
                flash('Invalid Password.', 'error')
        else:
            flash('Invalid Email Address.', 'error')
    context = {"form": form}
    return render_template('user-login.html', context=context)

@webapp.route("/sign-up/", methods=['GET', 'POST'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard_page'))

    form = RegistrationForm()
    if request.method == 'POST':
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            #print(f'{form.username.data}-{form.email.data}-{form.password.data}')
            flash('Sign Up Successful.', 'success')
            return redirect(url_for('webapp.login_page'))
        except IntegrityError:
            db.session.rollback()
            flash('Email is already in use.', 'error')

    context = {"form": form}
    return render_template('user-register.html', context=context)

@webapp.route("/logout/", methods=['GET', 'POST'])
@login_required
def logout():
    discord.revoke()
    for key in list(session.keys()):
        session.pop(key)
    session.clear()
    logout_user()
    flash('Log Out Successful.', 'success')
    return redirect(url_for('webapp.login_page'))

@webapp.route("/music/") #released music
def music_page():
    return "<p>Hello, World!</p>"
