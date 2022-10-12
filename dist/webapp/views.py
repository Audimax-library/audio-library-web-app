from urllib import request
from flask import Blueprint,render_template, redirect, session, url_for, request as rq, make_response
from .forms import UploadFileForm
from .models import Release
from werkzeug.utils import secure_filename
import os
from uuid import uuid4
from webapp import db

webapp = Blueprint('webapp', __name__, static_folder="static", static_url_path='/webapp/static' , template_folder='templates')
UPLOAD_FOLDER = "static/uploads/"

def make_unique(string):
    ident = uuid4().__str__()
    return f"{ident}-{string}"

@webapp.route("/", methods=['GET', 'POST'])
@webapp.route("/home", methods=['GET', 'POST'])
def home_page():
    fileForm = UploadFileForm()
    if(fileForm.validate_on_submit()):
        file = fileForm.file.data
        sec_filename = secure_filename(file.filename)
        split_tup = os.path.splitext(sec_filename)
        dest_filename = make_unique(f'main_upload{split_tup[1]}')
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),UPLOAD_FOLDER, dest_filename))
        insertQuery = Release(title=fileForm.title.data, artist=fileForm.artist.data, cover_img=dest_filename, description=fileForm.description.data)
        db.session.add(insertQuery)
        db.session.commit()
        return redirect('/home')
        
    music = Release.query.all()
    context = {
        'form': fileForm,
        'latest_releases': music,
        }
    return render_template('home.html', context=context)

from flask_login import login_required, login_user, logout_user, current_user
from admin import db, login_manager, oauth, discord, bcrypt
from admin.forms import LoginForm, RegistrationForm
from admin.models import User
from datetime import timedelta

login_manager.login_view = "webapp.login_page"
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@webapp.route("/login", methods=['GET', 'POST'])
def login_page():
    if session.get('profile'):
        user_detail = session['profile']
        print(user_detail['name'])
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard_page'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print(rq.form.getlist('rememberme'))
        if(user):
            if(bcrypt.check_password_hash(user.password, form.password.data)):
                login_user(user, remember=True, duration=timedelta(days=30))
                return redirect(url_for('admin.dashboard_page'))
    context = {"form": form}
    return render_template('user-login.html', context=context)

@webapp.route("/sign-up", methods=['GET', 'POST'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard_page'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('webapp.login_page'))

    context = {"form": form}
    return render_template('user-register.html', context=context)


@webapp.route("/music") #released music
def music_page():
    return "<p>Hello, World!</p>"
