from flask import Blueprint,render_template, redirect
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

@webapp.route("/blog") #new announcements and stuf
def blog_page():
    music = Release.query.all()
    print(music)
    return "<p>Hello, World!</p>"

@webapp.route("/music") #released music
def music_page():
    return "<p>Hello, World!</p>"

@webapp.route("/use-it") #guidelines to use music and FAQ
def use_music_page():
    return "<p>Hello, World!</p>"

@webapp.route("/about") #about/donate
def about_page():
    return "<p>Hello, World!</p>"
