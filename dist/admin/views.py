from flask import Blueprint,render_template, redirect, url_for, session
from .forms import RegistrationForm, LoginForm
from .models import User 
from admin import db, login_manager, oauth, discord, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
import os

admin = Blueprint('admin', __name__, static_folder="static", static_url_path="/admin/static" , template_folder='templates')
login_manager.login_view = "admin.home_page"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@admin.route("/", methods=['GET', 'POST'])
def home_page():
    if session.get('profile'):
        user_detail = session['profile']
        print(user_detail['name'])
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard_page'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if(user):
            if(bcrypt.check_password_hash(user.password, form.password.data)):
                login_user(user)
                return redirect(url_for('admin.dashboard_page'))
    context = {"form": form}
    return render_template('login.html', context=context)

@admin.route("/register", methods=['GET', 'POST'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard_page'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('admin.home_page'))

    context = {"form": form}
    return render_template('register.html', context=context)

@admin.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    discord.revoke()
    for key in list(session.keys()):
        session.pop(key)
    session.clear()
    logout_user()
    return redirect(url_for('admin.home_page'))

@admin.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard_page():
    context = {'user':current_user}
    return render_template('dashboard.html', context=context)

#### google OAuth
@admin.route('/oauth')
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
    redirect_uri = url_for('admin.authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@admin.route('/authorize')
def authorize():
    token = oauth.google.authorize_access_token()
    user = oauth.google.userinfo()
    session['profile'] = user
    userQuery = User.query.filter_by(email=user['email']).first()
    if(userQuery):
        login_user(userQuery)
        return redirect(url_for('admin.dashboard_page'))
    return redirect(url_for('admin.home_page'))  # make the session permanant so it keeps existing after broweser gets closed

#### Discord OAuth
@admin.route("/discordlogin/")
def discord_login():
    return discord.create_session()

@admin.route("/me/")
def me():
    try:
        user = discord.fetch_user()
        print(user.email)
    except:
        return redirect(url_for('admin.discord_login'))
    return f"""
<html>
<head>
<title>{user.email}</title>
</head>
<body><img src='{user.avatar_url or user.default_avatar_url}' />
<p>Is avatar animated: {str(user.is_avatar_animated)}</p>
<a href={url_for("admin.home_page")}>admin</a>
<br />
</body>
</html>
"""

@admin.route("/discord-authorize/")
def callback():
    data = discord.callback()
    #print(data)
    redirect_to = data.get("redirect", "/")

    user = discord.fetch_user()
    userQuery = User.query.filter_by(email=user.email).first()
    if(userQuery):
        login_user(userQuery)
        return redirect(url_for('admin.dashboard_page'))
    return redirect(url_for('admin.home_page'))
