from flask import Blueprint,render_template, redirect, session, url_for, request, make_response, jsonify, abort, flash
from .forms import UploadFileForm
from werkzeug.utils import secure_filename
from uuid import uuid4
from webapp import db
from flask_login import login_required, login_user, logout_user, current_user
from admin import db, login_manager, oauth, discord, bcrypt
from admin.forms import LoginForm, RegistrationForm
from admin.models import User
import datetime, json, re, os, threading, phonetics, requests, random, markdown
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, or_, func
from sqlalchemy.dialects.mysql import insert #only works with mysql
from .models import Genre, Book, Chapter, NewsLetterSubscription, Library, Rating, ReportBook, ListenHistory, Announcement
from .send_email import send_mail
from urllib.parse import parse_qs, urlparse
from admin.views import is_allowed


webapp = Blueprint('webapp', __name__, static_folder="static", static_url_path='/webapp/static' , template_folder='templates')
UPLOAD_FOLDER = "static/uploads/"
CHAPTER_UPLOAD_FOLDER = "static/uploads/chapters/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav'}
RECAPTCHA_VERIFY_URL='https://www.google.com/recaptcha/api/siteverify'
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
        dist_item = {"id": item.id, "title":item.title, "cover_img":item.cover_img, "status":item.status, "no_chapters": len(item.chapters)}
        dist_list.append(dist_item)
    return dist_list

def check_email(str_val):
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.match(pat,str_val):
        return True
    else:
        return False

def filter_books(obj, status_list, genre_list):
    return_book_list = []
    for book in obj:
        book_genre_list = book.genres
        if status_list == []:
           for genre in book_genre_list:
                if(str(genre.id) in genre_list):
                    return_book_list.append(book)
                    break
        else:
            print(book_genre_list)
            if(book.status in status_list):
                if genre_list == []:
                    return_book_list.append(book)
                    continue
                for genre in book_genre_list:
                    if(str(genre.id) in genre_list):
                        return_book_list.append(book)
                        break
    return return_book_list


######## 404 page
""" @webapp.errorhandler(404)
def page_not_found(e):
    context = {}
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
        #user = User.query.filter_by(email=str(current_user)).first()
        context['user_name'] = current_user.username
    return render_template('404.html', context=context), 404 """

######## home page
@webapp.route("/home/", methods=['GET', 'POST'])
@webapp.route("/", methods=['GET', 'POST'])
def home_page():
    recent_books = Book.query.filter_by(is_approved=1).order_by(desc(Book.created)).limit(8).all()
    recent_chapters = Chapter.query.order_by(desc(Chapter.created)).limit(20).all()
    context = {
        'recent_books':recent_books,
        'recent_chapters':recent_chapters,
    }
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
        #user = User.query.filter_by(email=str(current_user)).first()
        context['user_name'] = current_user.username
    return render_template('home.html', context=context)

######## newsletter endpoint
@webapp.route("/newsletter/", methods=['POST'])
def newsletter_endpoint():
    if request.method == 'POST':
        news_letter_data = request.get_json()
        user_email = news_letter_data['mail']
        if check_email(user_email):
            try:
                tempNewsletter = NewsLetterSubscription(
                    email=user_email
                )
                db.session.add(tempNewsletter)
                db.session.commit()
                thread = threading.Thread(target=send_mail, args=(user_email,))
                thread.start()
                return jsonify({'user_email': user_email,'exist': 'added'})
            except IntegrityError:
                db.session.rollback()
                return jsonify({'user_email': user_email,'exist': 'exists'})
            except:
                return jsonify({'user_email': user_email,'exist': 'error'})
        else:
            return jsonify({'user_email': user_email,'exist': 'error'})

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
    if not(is_allowed(current_user, allowed_roles=[1,2])):
        return redirect(url_for('webapp.home_page'))
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
                        Book.author_name: update_title_author,
                        Book.is_approved: 1
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
                    Book.author_name: update_title_author,
                    Book.is_approved: 1
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
        Book.author_name.ilike(f'%{search_by}%')),
        Book.is_approved==1).all()
    #results = db.session.query(Book).all()
    context={
        "result": "success",
        "value": book_obj_to_dist(results),
    }
    return jsonify(context)

######## search titles
@webapp.route("/titles/", methods=['GET', 'POST'])
def titles_page():
    if request.method == 'POST':
        data = request.get_json()['data']
        data_dict = parse_qs(data)
        search_by = request.get_json()['query']
        results = db.session.query(Book).filter(or_(
            Book.title.ilike(f'%{search_by}%'), 
            Book.alt_title.ilike(f'%{search_by}%'), 
            Book.synopsis.ilike(f'%{search_by}%'), 
            Book.author_name.ilike(f'%{search_by}%')),
            Book.is_approved==1).all()
        if "status" in data_dict and "genres" in data_dict:
            filtered_books = filter_books(results, data_dict['status'], data_dict['genres'])
        elif "status" in data_dict:
            filtered_books = filter_books(results, data_dict['status'], [])
        elif "genres" in data_dict:
            filtered_books = filter_books(results, [], data_dict['genres'])
        else:
            filtered_books = results
        json_context={
            "result": "success",
            "value": book_obj_to_dist(filtered_books),
        }
        return jsonify(json_context)
    param1 = request.args.get('q')
    param2 = request.args.getlist('status')
    param3 = request.args.getlist('genres')
    #print(f'{param1}\n{param2}\n{param3}\n')
    genre_list = Genre.query.all()
    context = {
        'search_query': param1,
        'status_query': param2,
        'genres_query': param3,
        'genres': genre_list,
        'status_types': status_types,
    }
    if param1:
        results = db.session.query(Book).filter(or_(
            Book.title.ilike(f'%{param1}%'), 
            Book.alt_title.ilike(f'%{param1}%'), 
            Book.synopsis.ilike(f'%{param1}%'), 
            Book.author_name.ilike(f'%{param1}%')),
            Book.is_approved==1).all()
    else:
        results = Book.query.filter_by(is_approved=1).order_by(desc(Book.created)).limit(15).all()
    if param2 != [] and param3 != []:
        filtered_books = filter_books(results, param2, param3)
    elif param2 != []:
        filtered_books = filter_books(results, param2, [])
    elif param3 != []:
        filtered_books = filter_books(results, [], param3)
    else:
        filtered_books = results
    context['results'] = filtered_books
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
        context['user_name'] = current_user.username
    return render_template('search-titles.html', context=context)


######## random title
@webapp.route("/titles/random/", methods=['GET', 'POST'])
def random_title():
    book_details = Book.query.filter_by(is_approved=1).all()
    if(book_details != []):
        random_book = random.choice(book_details)
        return redirect(url_for('webapp.book_page', id=random_book.id))
    else:
        flash("There's no books to get a random book title.", 'error')
        return redirect(url_for('webapp.home_page'))

######## view title
@webapp.route("/book/<int:id>/", methods=['GET', 'POST'])
def book_page(id):
    book_details = Book.query.get_or_404(id)
    if book_details.is_approved == 0:
        flash("You are not authorized to view this page.", 'error')
        abort(404)
    library_count = Library.query.filter_by(book_id=id).count()
    rating_total = db.session.query(
        func.sum(Rating.rate_score).label('rating_sum'),
        func.count().label('no_rows')
        ).filter_by(book_id=id).first()
    rating_avg = 0
    if rating_total.no_rows:
        rating_avg = rating_total.rating_sum/rating_total.no_rows
    context = {
        'book_details': book_details,
        'library_total': library_count,
        'rating_avg': rating_avg,
        'site_key': os.getenv('RECAPTCHA_SITE_KEY'),
        }
    if current_user.is_authenticated:
        library_data = Library.query.filter_by(book_id=id,user_email=str(current_user)).first()
        rating_data = Rating.query.filter_by(book_id=id,user_email=str(current_user)).first()
        if library_data:
            context['library_added'] = True
        if rating_data:
            context['book_rating'] = rating_data.rate_score
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

######## View Chapter
@webapp.route("/book/<int:book_id>/listen/<int:chapter_id>/", methods=['GET', 'POST'])
def view_chapter(book_id,chapter_id):
    book_details = Book.query.get_or_404(book_id)
    chapter_details = Chapter.query.get_or_404(chapter_id)
    if book_details.is_approved == 0:
        flash("You are not authorized to view this page.", 'error')
        abort(404)
    context = {
        "book_details": book_details,
        "chapter_details": chapter_details,
    }
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
        context['user_name'] = current_user.username
    return render_template('player.html', context=context)


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

######## add to library
@webapp.route("/book/add-to-library/", methods=['POST'])
def add_to_library():
    if request.method == 'POST':
        if current_user.is_authenticated:
            data = request.get_json()['book_id']
            try:
                tempLibrary = Library(
                    book_id=data,
                    user_email=str(current_user),
                )
                db.session.add(tempLibrary)
                db.session.commit()
                return jsonify({'status': 'success', 'value':'added'})
            except IntegrityError:
                db.session.rollback()
                db.session.query(Library).filter_by(book_id=data,user_email=str(current_user)).delete()
                db.session.commit()
                return jsonify({'status': 'success', 'value':'removed'})
            except:
                abort(400, 'Error: Insert DB error.')
        else:
            print('Invalid Request: You have to be logged in to add books to library!')
            flash('You have to be logged in to add books to library!', 'error')
            return jsonify({'status': 'unauthorized', 'value':'redirect'})


######## Rate Book
@webapp.route("/book/rate/", methods=['POST'])
def rate_book():
    if request.method == 'POST':
        if current_user.is_authenticated:
            data_book_id = request.get_json()['book_id']
            data_rate_val = request.get_json()['rate_val']
            try:
                tempRating = Rating(
                    book_id=data_book_id, 
                    user_email=str(current_user), 
                    rate_score=data_rate_val
                )
                db.session.add(tempRating)
                db.session.commit()
                return jsonify({'status': 'success', 'value':'rated'})
            except IntegrityError:
                db.session.rollback()
                ratingRec = db.session.query(Rating).filter_by(book_id=data_book_id,user_email=str(current_user)).first()
                ratingRec.rate_score = data_rate_val
                db.session.commit()
                return jsonify({'status': 'success', 'value':'updated'})
            except:
                abort(400, 'Error: Insert DB error.')
        else:
            print('Invalid Request: You have to be logged in to rate books!')
            flash('You have to be logged in to rate books!', 'error')
            return jsonify({'status': 'unauthorized', 'value':'redirect'})

######## Report Book
@webapp.route("/book/report/<int:id>/", methods=['POST'])
def report_book(id):
    if request.method == 'POST':
        secret_response = request.form['g-recaptcha-response']
        verify_response = requests.post(url=f'{RECAPTCHA_VERIFY_URL}?secret={os.getenv("RECAPTCHA_SECRET_KEY")}&response={secret_response}').json()
        if current_user.is_authenticated and verify_response['success'] == True:
            try:
                user_email = request.form['report-email']
                report_title = request.form['report-title']
                subject = request.form['report-subject']
                tempReport = ReportBook(
                    user_email=user_email,
                    title=report_title,
                    subject=subject,
                )
                db.session.add(tempReport)
                db.session.commit()
                flash('Issue reported successfully, an admin will contact you via email if needed.', 'success')
                return redirect(url_for('webapp.book_page', id=id))
            except:
                flash('An error occured while reporting the issue. Please try again later.', 'error')
                return redirect(url_for('webapp.book_page', id=id))
        else:
            flash('User has to be logged in to report issues.', 'error')
            return redirect(url_for('webapp.login_page'))
    return redirect(url_for('webapp.book_page', id=id))

######## add to playback history
@webapp.route("/book/history/", methods=['POST'])
def add_history():
    if request.method == 'POST':
        if current_user.is_authenticated:
            data_chapter_id = request.get_json()['chapter_id']
            try:
                tempHistory = ListenHistory(
                    user_email=str(current_user), 
                    chapter_id=int(data_chapter_id)
                )
                db.session.add(tempHistory)
                db.session.commit()
                return jsonify({'status': 'success', 'value':'added'})
            except IntegrityError:
                db.session.rollback()
                historyRec = db.session.query(ListenHistory).filter_by(user_email=str(current_user),chapter_id=int(data_chapter_id)).first()
                historyRec.last_heard_on = db.func.now()
                db.session.commit()
                return jsonify({'status': 'success', 'value':'updated'})
            except:
                abort(400, 'Error: Insert DB error.')
        else:
            print('Invalid Request: You have to be logged in to keep playback history!')
            flash('You have to be logged in to keep playback history!', 'error')
            return jsonify({'status': 'unauthorized', 'value':'redirect'})

######## Announcements page
@webapp.route("/announcements/", methods=['GET', 'POST'])
def announce_page():
    all_announce = Announcement.query.order_by(desc(Announcement.created_date)).all()
    context = {
        "all_announce": all_announce,
    }
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
        context['user_name'] = current_user.username
    return render_template('announcements.html', context=context)

######## privacy policy page
@webapp.route("/privacy-policy/", methods=['GET', 'POST'])
def policy_page():
    context = {}
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
        context['user_name'] = current_user.username
    return render_template('privacy-policy.html', context=context)

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
                if(user.is_banned == 0):
                    if(len(request.form.getlist('rememberme')) > 0):
                        login_user(user, remember=True, duration=datetime.timedelta(days=30))
                    else:
                        login_user(user)
                    flash(f'Welcome back, {user.username}.', 'success')
                    return redirect(url_for('webapp.home_page'))
                else:
                    flash("Your account has been banned due to suspicious activity.", 'error')
                    return redirect(url_for('webapp.home_page'))
            else:
                flash('Invalid Password.', 'error')
        else:
            flash('Invalid Email Address.', 'error')
    context = {"form": form}
    return render_template('user-login.html', context=context)

######## user sign up page 
@webapp.route("/sign-up/", methods=['GET', 'POST'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('webapp.profile_page'))

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

#### google OAuth
@webapp.route('/oauth')
def oauth_login():
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
     
    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
     
    # Redirect to google_auth function
    redirect_uri = url_for('webapp.authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@webapp.route('/authorize')
def authorize():
    token = oauth.google.authorize_access_token()
    user = oauth.google.userinfo()
    session['profile'] = user
    userQuery = User.query.filter_by(email=user['email']).first()
    if(userQuery):
        if(userQuery.is_banned == 0):
            login_user(userQuery, remember=True, duration=datetime.timedelta(days=7))
            flash(f'Welcome back, {userQuery.username}.', 'success')
            return redirect(url_for('webapp.home_page'))
        else:
            flash("Your account has been banned due to suspicious activity.", 'error')
            return redirect(url_for('webapp.home_page'))
    flash('This email is not a registered email. Please sign up first to use SSO.', 'error')
    return redirect(url_for('webapp.login_page'))

######## user logout redirect 
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

####### User profile
@webapp.route('/profile/')
def profile_page():
    context = {}
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
        context['user_name'] = current_user.username
        user_details = User.query.filter_by(email=str(current_user)).first()
        if user_details:
            library_details = Library.query.filter_by(user_email=str(current_user)).limit(50).all()
            upload_details = Chapter.query.filter_by(uploaded_by=str(current_user)).order_by(desc(Chapter.created)).limit(50).all()
            history_details = ListenHistory.query.filter_by(user_email=str(current_user)).order_by(desc(ListenHistory.last_heard_on)).limit(50).all()
            pending_drafts = Book.query.filter(Book.draft_user_email==str(current_user), Book.is_approved==0).limit(25).all()
            approved_drafts = Book.query.filter(Book.draft_user_email==str(current_user), Book.is_approved==1).limit(25).all()
            report_details = ReportBook.query.filter_by(user_email=str(current_user)).order_by(desc(ReportBook.created_date)).limit(10).all()
            context['user_details'] = user_details
            context['library_details'] = library_details
            context['upload_details'] = upload_details
            context['history_details'] = history_details
            context['pending_drafts'] = pending_drafts
            context['approved_drafts'] = approved_drafts
            context['report_details'] = report_details
        else:
            return redirect(url_for('webapp.login_page')) 
    else:
       return redirect(url_for('webapp.login_page')) 
    return render_template('user-profile.html', context=context)

####### API functions

@webapp.route("/v1/books/", methods=['GET'])
def book_api():
    results = Book.query.filter_by(is_approved=1).order_by(desc(Book.created)).all()
    if request.method == 'GET':
        param1 = request.args.get('query')
        if not param1 is None:
            book_list = []
            for word in param1.split(" "):
                phonetic_key = phonetics.dmetaphone(word)
                #print(f"{phonetic_key}")
                for book in results:
                    for chapter_title in book.title.split(" "):
                        title_key = phonetics.dmetaphone(chapter_title)
                        #print(f"{title_key[0]} - {phonetic_key[0]}")
                        if title_key[0] == phonetic_key[0]:
                            book_list.append(book)
                            continue
            filtered_book_list = list(set(book_list))
            filtered_json = book_obj_to_dist(filtered_book_list[:9])
            return jsonify({
                'status': '200',
                'books': filtered_json,
            })  
    return jsonify({
        'status': '200',
        'books': book_obj_to_dist(results[:9]),
    })

@webapp.route("/v1/books/<int:book_id>/", methods=['GET'])
def book_details_api(book_id):
    book_details = Book.query.get(book_id)
    #print(book_details)
    #print(request.remote_addr)
    if not book_details is None:
        dist_sub_item = []
        for chapter in book_details.chapters:
            dist_sub_item.append({"id": chapter.id, "order_number":chapter.display_number, "audio_url":"/webapp/static/uploads/chapters/"+chapter.audio_url})
        book_detail_dict = {"id": book_details.id, "title":book_details.title, "cover_img":book_details.cover_img, "status":book_details.status, "chapters": dist_sub_item}
        return jsonify({
            'status': '200',
            'books': book_detail_dict,
        })
    return jsonify({
        'status': '400',
        'messages': "A valid book id is required.",
    })
