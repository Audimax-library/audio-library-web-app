from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from flask_discord import DiscordOAuth2Session
from flask_bcrypt import Bcrypt

#from run import app

db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()
discord = DiscordOAuth2Session()
bcrypt = Bcrypt()
