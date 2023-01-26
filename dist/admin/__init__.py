from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from flask_discord import DiscordOAuth2Session
from flask_bcrypt import Bcrypt
import os

#from run import app
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI')
db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()
discord = DiscordOAuth2Session(redirect_uri=DISCORD_REDIRECT_URI)
bcrypt = Bcrypt()
