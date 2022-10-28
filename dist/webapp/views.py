from urllib import request
from flask import Blueprint,render_template, redirect, session, url_for, request as rq, make_response, jsonify
from .forms import UploadFileForm
from .models import Release
from werkzeug.utils import secure_filename
import os
from uuid import uuid4
from webapp import db
from flask_login import login_required, login_user, logout_user, current_user
from admin import db, login_manager, oauth, discord, bcrypt
from admin.forms import LoginForm, RegistrationForm
from admin.models import User
import datetime

webapp = Blueprint('webapp', __name__, static_folder="static", static_url_path='/webapp/static' , template_folder='templates')
UPLOAD_FOLDER = "static/uploads/"
login_manager.login_view = "webapp.login_page"

def make_unique(string):
    ident = uuid4().__str__()
    return f"{ident}-{string}"

@webapp.route("/", methods=['GET', 'POST'])
@webapp.route("/home/", methods=['GET', 'POST'])
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
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
    return render_template('home.html', context=context)

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
        print(user_detail['name'])
    if current_user.is_authenticated:
        return redirect(url_for('webapp.home_page'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print(rq.form.getlist('rememberme'))
        if(user):
            if(bcrypt.check_password_hash(user.password, form.password.data)):
                if(len(rq.form.getlist('rememberme')) > 0):
                    login_user(user, remember=True, duration=datetime.timedelta(days=30))
                else:
                    login_user(user)
                return redirect(url_for('webapp.home_page'))
    context = {"form": form}
    return render_template('user-login.html', context=context)

@webapp.route("/sign-up/", methods=['GET', 'POST'])
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

@webapp.route("/logout/", methods=['GET', 'POST'])
@login_required
def logout():
    discord.revoke()
    for key in list(session.keys()):
        session.pop(key)
    session.clear()
    logout_user()
    return redirect(url_for('webapp.login_page'))

@webapp.route("/music/") #released music
def music_page():
    return "<p>Hello, World!</p>"
