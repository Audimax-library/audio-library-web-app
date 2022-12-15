from flask import Blueprint,render_template, redirect, session, url_for, request, make_response, jsonify, abort, flash
from .forms import UploadFileForm
from werkzeug.utils import secure_filename
import os
from uuid import uuid4
from webapp import db
from flask_login import login_required, login_user, logout_user, current_user
from admin import db, login_manager, oauth, discord, bcrypt
from admin.forms import LoginForm, RegistrationForm
from admin.models import User
import datetime, json
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, or_
from .models import Genre, Book, Chapter

webapp = Blueprint('webapp', __name__, static_folder="static", static_url_path='/webapp/static' , template_folder='templates')
UPLOAD_FOLDER = "static/uploads/"
CHAPTER_UPLOAD_FOLDER = "static/uploads/chapters/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav'}
login_manager.login_view = "webapp.login_page"
status_types = ['Ongoing', 'Completed', 'Hiatus', 'Discontinued']
lang_types = ['Sinhala', 'English']


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def make_unique(string):
    ident = uuid4().__str__()
    return f"{ident}-{string}"

def allowed_file(filename, filetype):
    if filetype == 'image':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    else:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

def book_obj_to_dist(obj):
    dist_list = []
    for item in obj:
        dist_item = {"id": item.id, "title":item.title, "cover_img":item.cover_img, "status":item.status}
        dist_list.append(dist_item)
    return dist_list

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
        new_title_genre = request.form.getlist('new-title-genre')
        new_title_status = request.form['new-title-status']
        new_title_lang = request.form['new-title-lang']
        new_title_author = request.form['new-title-author']
        if new_title_cover and allowed_file(new_title_cover.filename, 'image'):
            filename = secure_filename(new_title_cover.filename)
            split_tup = os.path.splitext(filename)
            dest_filename = make_unique(f'new_title_cover{split_tup[1]}')
            try:
                new_title_cover.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),UPLOAD_FOLDER, dest_filename))
                new_title_query = Book(
                    title=new_title, 
                    alt_title=new_alt_title, 
                    cover_img=dest_filename, 
                    synopsis=new_title_synopsis, 
                    status=new_title_status, 
                    language=new_title_lang, 
                    author_name=new_title_author, 
                    draft_user_email=str(current_user))
                for item in new_title_genre:
                    genre_obj = db.session.query(Genre).filter_by(id=item).first()
                    new_title_query.genres.append(genre_obj)
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
    genres = Genre.query.all()
    context = {'genres':genres}
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
        context['user_name'] = current_user.username
    else:
        flash('You have to be logged in to your account.', 'error')
        return redirect(url_for('webapp.login_page'))
    return render_template('new-title.html', context=context)

######## update titles
@webapp.route("/book/<int:id>/edit/", methods=['GET', 'POST'])
def update_title_page(id):
    if request.method == 'POST':
        current_details = db.session.query(Book).filter_by(id=id)
        update_title = request.form['new-title']
        update_alt_title = request.form['new-alt-title']
        update_title_cover = request.files['new-title-cover']
        update_title_synopsis = request.form['new-title-synopsis']
        update_title_genre = request.form.getlist('new-title-genre')
        update_title_status = request.form['new-title-status']
        update_title_lang = request.form['new-title-lang']
        update_title_author = request.form['new-title-author']
        genre_obj_list = db.session.query(Genre).filter(Genre.id.in_(update_title_genre)).all()
        if update_title_cover:
            if allowed_file(update_title_cover.filename, 'image'):
                filename = secure_filename(update_title_cover.filename)
                split_tup = os.path.splitext(filename)
                dest_filename = db.session.query(Book).filter_by(id=id).first().cover_img
                try:
                    update_title_cover.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),UPLOAD_FOLDER, dest_filename))
                    current_details.update({
                        Book.cover_img: dest_filename,
                        Book.title: update_title, 
                        Book.alt_title: update_alt_title, 
                        Book.synopsis: update_title_synopsis,
                        Book.status: update_title_status, 
                        Book.language: update_title_lang, 
                        Book.author_name: update_title_author
                        })
                    db.session.commit()
                    current_details = db.session.query(Book).filter_by(id=id).first()
                    current_genre_list = []
                    for i in current_details.genres:
                        current_genre_list.append(i)
                    for item1 in current_genre_list:
                        #print(f'remove{item1.title}')
                        current_details.genres.remove(item1)
                    for item2 in genre_obj_list:
                        #print(f'add{item2.title}')
                        current_details.genres.append(item2)
                    db.session.commit()
                    flash('Update title successful.', 'success')
                    return redirect(url_for('webapp.book_page', id=id))
                except Exception as e:
                    flash('An error occured while saving the cover image. Please try again later.', 'error')
                    print(e)
                    return redirect(url_for('webapp.book_page', id=id))
            else:
                flash('Invalid file type. (Allowed only JPG, JPEG, PNG)', 'error')
                return redirect(url_for('webapp.book_page', id=id))
        else:
            print("non-image here")
            try:
                current_details.update({
                    Book.title: update_title, 
                    Book.alt_title: update_alt_title, 
                    Book.synopsis: update_title_synopsis,
                    Book.status: update_title_status, 
                    Book.language: update_title_lang, 
                    Book.author_name: update_title_author
                    })
                db.session.commit()
                current_details = db.session.query(Book).filter_by(id=id).first()
                current_genre_list = []
                for i in current_details.genres:
                    current_genre_list.append(i)
                for item1 in current_genre_list:
                    #print(f'remove{item1.title}')
                    current_details.genres.remove(item1)
                for item2 in genre_obj_list:
                    #print(f'add{item2.title}')
                    current_details.genres.append(item2)
                db.session.commit()
                flash('Update title successful.', 'success')
                return redirect(url_for('webapp.book_page', id=id))
            except Exception as e:
                flash('An error occured while updating the database. Please try again later.', 'error')
                print(e)
                return redirect(url_for('webapp.book_page', id=id))
    genres = Genre.query.all()
    book_details = Book.query.get_or_404(id)
    context = {
        'book_details': book_details,
        'genres':genres,
        'status_types':status_types,
        'lang_types':lang_types,
    }
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
        context['user_name'] = current_user.username
    else:
        flash('You have to be logged in to your account.', 'error')
        return redirect(url_for('webapp.login_page'))
    if current_user.email == book_details.draft_user_email:
        return render_template('update-title.html', context=context)
    else:
        flash('You are not authorized for this action.', 'error')
        return redirect(url_for('webapp.home_page'))

######## quick search titles/ajax endpoint
@webapp.route("/search/titles/", methods=['POST'])
def title_quick_search():
    data = request.get_json()
    search_by  = data['data']
    results = db.session.query(Book).filter(or_(
        Book.title.ilike(f'%{search_by}%'), 
        Book.alt_title.ilike(f'%{search_by}%'), 
        Book.synopsis.ilike(f'%{search_by}%'), 
        Book.author_name.ilike(f'%{search_by}%'))).all()
    #results = db.session.query(Book).all()
    print()
    context={
        "result": "success",
        "value": book_obj_to_dist(results),
    }
    return jsonify(context)

######## search titles
@webapp.route("/titles/", methods=['GET', 'POST'])
def titles_page():
    query = request.args.get('q')
    return f'<h1>{query}</h1>'

######## newsletter data
@webapp.route("/newsletter/", methods=['POST'])
def newsletter_endpoint():
    if request.method == 'POST':
        data = request.get_json()
        user_email = data['data']
        print(user_email)
        return jsonify({'user_email':user_email})

######## view title
@webapp.route("/book/<int:id>/", methods=['GET', 'POST'])
def book_page(id):
    book_details = Book.query.get_or_404(id)
    context = {
        'book_details': book_details,
        }
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
        context['user_name'] = current_user.username
    return render_template('book.html', context=context)

######## Upload new chapter
@webapp.route("/book/<int:id>/upload/", methods=['GET', 'POST'])
def upload_chapter(id):
    if request.method == 'POST':
        chapter_title = request.form['title']
        chapter_title_id = request.form['title-id']
        chapter_order = request.form['chapter-order']
        chapter_display = request.form['chapter-display']
        chapter_audio_file = request.files['audio-file']
        if chapter_audio_file and allowed_file(chapter_audio_file.filename, 'audio'):
            filename = secure_filename(chapter_audio_file.filename)
            split_tup = os.path.splitext(filename)
            dest_filename = make_unique(f'{chapter_title_id}_chapter_{split_tup[1]}')
            try:
                chapter_audio_file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),CHAPTER_UPLOAD_FOLDER, dest_filename))
                try:
                    new_chapter_query = Chapter(
                        order = int(chapter_order),
                        display_number = chapter_display,
                        audio_url=dest_filename,
                        is_convert=0,
                        read_text_url='NULL',
                        uploaded_by=str(current_user),
                        book_id=chapter_title_id
                    )
                    db.session.add(new_chapter_query)
                    db.session.commit()
                    flash('New Chapter added successfully!', 'success')
                    return redirect(url_for('webapp.book_page', id=chapter_title_id))
                except Exception as e:
                    flash('An error occured while updating the database. Please try again later.', 'error')
                    print(e)
                    return redirect(url_for('webapp.home_page'))
            except Exception as e:
                flash('An error occured uploading the audio file. Please try again later.', 'error')
                print(e)
                return redirect(url_for('webapp.home_page'))
    book_details = Book.query.get_or_404(id)
    context = {'book_details': book_details}
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
        context['user_name'] = current_user.username
    else:
        flash('You have to be logged in to your account.', 'error')
        return redirect(url_for('webapp.login_page'))
    return render_template('new-chapter.html', context=context)

######## Delete chapter
@webapp.route("/book/<int:book_id>/delete/<int:chapter_id>/", methods=['POST'])
def update_chapter(book_id,chapter_id):
    if request.method == 'POST':
        if current_user.is_authenticated:
            try:
                #os.remove(f"/static/uploads/chapters/{db.session.query(Chapter).filter_by(id=chapter_id).first().audio_url}")
                db.session.query(Chapter).filter_by(id=chapter_id).delete()
                db.session.commit()
                flash('Chapter deleted successfully!', 'success')
                return jsonify({'status': 'success'})
            except Exception as e:
                flash('An error occured deleting the chapter. Please try again later.', 'error')
                print(e)
                abort(400, 'Error: File delete Failed.')
        else:
            print('Invalid Request: Authentication Failed')
            flash('Authentication Failed!', 'error')
            abort(400, 'Error: Authentication Failed.')

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
