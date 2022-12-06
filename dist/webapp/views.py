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
from sqlalchemy import desc
from .models import Book_type, Book

webapp = Blueprint('webapp', __name__, static_folder="static", static_url_path='/webapp/static' , template_folder='templates')
UPLOAD_FOLDER = "static/uploads/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
login_manager.login_view = "webapp.login_page"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def make_unique(string):
    ident = uuid4().__str__()
    return f"{ident}-{string}"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

######## home page
@webapp.route("/", methods=['GET', 'POST'])
@webapp.route("/home/", methods=['GET', 'POST'])
def home_page():
    recent_books = Book.query.filter_by(is_approved=1).order_by(desc(Book.created)).limit(8).all()
    print(recent_books)
    context = {'recent_books':recent_books}
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
        #user = User.query.filter_by(email=str(current_user)).first()
        context['user_name'] = current_user.username
    return render_template('home.html', context=context)

######## add new title
@webapp.route("/add-titles/", methods=['GET', 'POST'])
def add_title_page():
    if request.method == 'POST':
        new_title = request.form['new-title']
        new_alt_title = request.form['new-alt-title']
        new_title_cover = request.files['new-title-cover']
        new_title_synopsis = request.form['new-title-synopsis']
        new_title_genre = request.form['new-title-genre']
        new_title_status = request.form['new-title-status']
        new_title_lang = request.form['new-title-lang']
        new_title_author = request.form['new-title-author']
        if new_title_cover and allowed_file(new_title_cover.filename):
            filename = secure_filename(new_title_cover.filename)
            split_tup = os.path.splitext(filename)
            dest_filename = make_unique(f'new_title_cover{split_tup[1]}')
            try:
                new_title_cover.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),UPLOAD_FOLDER, dest_filename))
                new_title_query = Book(title=new_title, 
                    alt_title=new_alt_title, 
                    cover_img=dest_filename, 
                    synopsis=new_title_synopsis, 
                    type_id=int(new_title_genre), 
                    status=new_title_status, 
                    language=new_title_lang, 
                    author_name=new_title_author, 
                    draft_user_email=str(current_user))
                db.session.add(new_title_query)
                db.session.commit()
            except Exception as e:
                flash('An error occured while creating the new title. Please try again later.', 'error')
                print(e)
                return redirect(url_for('webapp.add_title_page'))
            flash('New title has been created. Title will be approved within 24Hrs', 'success')
            return redirect(url_for('webapp.home_page'))
        else:
            print("Invalid file type")
            flash('Invalid file type. (Allowed only JPG, JPEG, PNG)', 'error')
            return redirect(url_for('webapp.add_title_page'))
    genres = Book_type.query.all()
    context = {'genres':genres}
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
        context['user_name'] = current_user.username
    else:
        return redirect(url_for('webapp.login_page'))
    return render_template('new-title.html', context=context)

######## search titles

@webapp.route("/titles/", methods=['GET', 'POST'])
def titles_page():
    query = request.args.get('q')
    return f'<h1>{query}</h1>'

######## view title
@webapp.route("/book/<int:id>/", methods=['GET', 'POST'])
def book_page(id):
    book_details = Book.query.get_or_404(id)
    book_type = Book_type.query.get_or_404(book_details.type_id)
    context = {
        'book_details': book_details,
        'book_type': book_type,
        }
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
        context['user_name'] = current_user.username
    return render_template('book.html', context=context)

######## user login page 
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
