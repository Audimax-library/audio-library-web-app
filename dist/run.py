from flask import Flask, render_template
from webapp import db as webapp_db
from admin import db as admin_db, login_manager, oauth, discord, bcrypt
from flask_login import current_user

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

db_user = os.getenv('DB_USER')
db_pswd = os.getenv('DB_PSWD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')


app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{db_user}:{db_pswd}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('APP_SEC')
app.config['UPLOAD_FOLDER'] = os.getenv('STATIC_UPLOAD')

# !! Only in development environment.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"

app.config["DISCORD_CLIENT_ID"] = os.getenv('DISCORD_CLIENT_ID')
app.config["DISCORD_CLIENT_SECRET"] = os.getenv('DISCORD_CLIENT_SECRET')
#app.config["DISCORD_BOT_TOKEN"] = ''
app.config["DISCORD_REDIRECT_URI"] = "http://127.0.0.1:5000/admin/discord-authorize"

webapp_db.init_app(app)
admin_db.init_app(app)
login_manager.init_app(app)
oauth.init_app(app)
discord.init_app(app)
bcrypt.init_app(app)


from webapp.views import webapp
from admin.views import admin
from assisted.views import assisted
app.register_blueprint(webapp, url_prefix="/")
app.register_blueprint(admin, url_prefix="/admin")
app.register_blueprint(assisted, url_prefix="/assisted")

######## 404 page
@app.errorhandler(404)
def page_not_found(e):
    context = {}
    if current_user.is_authenticated:
        context['user_initial'] = str(current_user)[0:2].upper()
        #user = User.query.filter_by(email=str(current_user)).first()
        context['user_name'] = current_user.username
    return render_template('404.html', context=context), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
