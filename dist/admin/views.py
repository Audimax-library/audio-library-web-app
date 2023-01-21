from flask import Blueprint,render_template, redirect, url_for, session, flash, request, jsonify
from .forms import RegistrationForm, LoginForm
from .models import User
from webapp.models import Book, Chapter, Genre, Announcement, ReportBook, NewsLetterSubscription
from webapp.send_email import send_newsletter, send_custom_newsletter
from admin import db, login_manager, oauth, discord, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import desc, or_, and_
import os, threading

admin = Blueprint('admin', __name__, static_folder="static", static_url_path="/admin/static" , template_folder='templates')
login_manager.login_view = "admin.home_page"

def is_allowed(user, allowed_roles=[]):
    if not(user.userlevel in allowed_roles) or user.is_banned:
        flash('Invalid URL.', 'error')
        return False
    return True

def user_obj_to_dist(obj):
    dist_list = []
    for item in obj:
        if item.is_banned:
            status_str = '<span class="badge rounded-pill bg-danger">Banned</span>';
        else:
            status_str = '<span class="badge rounded-pill bg-success">Active</span>';
        dist_item = {
            "id": item.id, 
            "userlevel":item.level_obj.title, 
            "username":item.username, 
            "email":item.email, 
            "is_banned": item.is_banned, 
            "created_on": item.created_on, 
            "status_element": status_str, 
            }
        dist_list.append(dist_item)
    return dist_list

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
            if(user.is_banned == 0):
                if(bcrypt.check_password_hash(user.password, form.password.data)):
                    login_user(user)
                    flash("Welcome back!.", 'success')
                    return redirect(url_for('admin.dashboard_page'))
            else:
                flash("Your account has been banned due to suspicious activity.", 'error')
                return redirect(url_for('admin.home_page'))
    context = {"form": form}
    return render_template('login.html', context=context)

@admin.route("/register/", methods=['GET', 'POST'])
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

@admin.route("/logout/", methods=['GET', 'POST'])
@login_required
def logout():
    discord.revoke()
    for key in list(session.keys()):
        session.pop(key)
    session.clear()
    logout_user()
    flash('Log Out Successful.', 'success')
    return redirect(url_for('admin.home_page'))

#
##
####### Dashboard page
@admin.route('/dashboard/', methods=['GET', 'POST'])
@login_required
def dashboard_page():
    if not(is_allowed(current_user, allowed_roles=[1,2])):
        return redirect(url_for('webapp.home_page'))
    context = {'user':current_user}
    return render_template('dashboard.html', context=context)

####### Title Drafts page
@admin.route('/dashboard/drafts/', methods=['GET', 'POST'])
@login_required
def drafts_page():
    if not(is_allowed(current_user, allowed_roles=[1,2])):
        return redirect(url_for('webapp.home_page'))
    if request.method == 'POST':
        try:
            new_title = request.form['book_id']
            current_details = db.session.query(Book).filter_by(id=new_title).first()
            current_details.is_approved = 1
            db.session.commit()
            flash('Title Approved successfully.', 'success')
            return redirect(url_for('admin.drafts_page'))
        except:
            flash('An error occured while updating the database.', 'error')
            return redirect(url_for('admin.dashboard_page'))
    draft_books = Book.query.filter_by(is_approved=0).order_by(desc(Book.created)).all()
    context = {
        'user':current_user,
        'draft_books':draft_books,

        }
    return render_template('draft_books.html', context=context)

####### Manage Books
@admin.route('/dashboard/books/', methods=['GET', 'POST'])
@login_required
def manage_books_page():
    if not(is_allowed(current_user, allowed_roles=[1,2])):
        return redirect(url_for('webapp.home_page'))
    if request.method == 'POST':
        try:
            data = request.get_json()
            new_title = data['book_id']
            new_state = data['change_val']
            #print(new_state)
            #print(new_title)
            current_details = db.session.query(Book).filter_by(id=int(new_title)).first()
            current_details.is_approved = int(new_state)
            db.session.commit()
            return jsonify({'status': 'success', 'value': 'updated'})
        except:
            return jsonify({'status': 'failed', 'value': 'failed'})
    draft_books = Book.query.filter_by(is_approved=0).order_by(desc(Book.created)).count()
    approved_books = Book.query.filter_by(is_approved=1).order_by(desc(Book.created)).all()
    context = {
        'user':current_user,
        'draft_book_count':draft_books,
        'approved_books':approved_books,
        }
    return render_template('manage_books.html', context=context)

####### Delete Books & Chapters
@admin.route('/dashboard/<string:type>/delete/<int:id>/', methods=['GET', 'POST'])
@login_required
def delete_page(type, id):
    if not(is_allowed(current_user, allowed_roles=[1,2])):
        return redirect(url_for('webapp.home_page'))
    if request.method == 'POST':
        item_type = request.form['item-type']
        item_id = request.form['item-id']
        if(item_type == "Title"):
            try:
                db.session.query(Book).filter_by(id=int(item_id)).delete()
                db.session.commit()
                flash('Title deleted successfully.', 'success')
            except:
                flash('An error occured while deleting from the database.', 'error')
        elif(item_type == "Chapter"):
            try:
                db.session.query(Chapter).filter_by(id=int(item_id)).delete()
                db.session.commit()
                flash('Chapter deleted successfully.', 'success')
            except:
                flash('An error occured while deleting from the database.', 'error')
        return redirect(url_for('admin.manage_books_page'))
    if(type == "Title"):
        item_details = db.session.query(Book).filter_by(id=int(id)).first()
    elif(type == "Chapter"):
        item_details = db.session.query(Chapter).filter_by(id=int(id)).first()
    context = {
        'user':current_user,
        'type':type,
        'item_details':item_details,
        }
    return render_template('delete_page.html', context=context)

####### Manage Users
@admin.route('/dashboard/user/', methods=['GET', 'POST'])
@login_required
def manage_users_page():
    if not(is_allowed(current_user, allowed_roles=[1,])):
        flash('You are not authorized to manage users.', 'error')
        return redirect(url_for('admin.home_page'))
    if request.method == 'POST':
        try:
            data = request.get_json()
            call_type = data['type']
            if call_type == 'search':
                search_by = data['value']
                results = db.session.query(User).filter(or_(
                    User.username.ilike(f'%{search_by}%'), 
                    User.email.ilike(f'%{search_by}%')), and_(
                    User.userlevel == 0 )).all()
                #print(results)
                context={
                    "status": "success",
                    "value": user_obj_to_dist(results),
                }
                return jsonify(context)
            elif call_type == 'role':
                change_value = data['change_value']
                user_id = data['user_id']
                current_details = db.session.query(User).filter_by(id=int(user_id)).first()
                current_details.userlevel = int(change_value)
                db.session.commit()
                flash('User auth level changed!','success')
                return jsonify({'status': 'success', 'value': 'updated'})
            elif call_type == 'ban':
                user_id = data['user_id']
                current_details = db.session.query(User).filter_by(id=int(user_id)).first()
                if(current_details.is_banned == 0):
                    current_details.is_banned = 1
                else:
                    current_details.is_banned = 0
                db.session.commit()
                flash("User's banned status has been changed!",'success')
                return jsonify({'status': 'success', 'value': 'updated'})
            elif call_type == 'kick':
                user_id = data['user_id']
                current_details = db.session.query(User).filter_by(id=int(user_id)).delete()
                db.session.commit()
                flash("User has been kicked from the platform!",'success')
                return jsonify({'status': 'success', 'value': 'updated'})
            return jsonify({'status': 'success', 'value': ""})
        except:
            return jsonify({'status': 'failed', 'value': 'failed'})
    all_staff = User.query.filter(User.userlevel != 0).order_by(desc(User.created_on)).all()
    all_member_count = User.query.filter(User.userlevel == 0).count()
    context = {
        'user':current_user,
        'all_staff':all_staff,
        'all_member_count':all_member_count,
        }
    return render_template('manage_users.html', context=context)

####### Manage genres
@admin.route('/dashboard/genre/', methods=['GET', 'POST'])
@login_required
def manage_genres_page():
    if not(is_allowed(current_user, allowed_roles=[1, 2])):
        flash('You are not authorized to manage users.', 'error')
        return redirect(url_for('admin.home_page'))
    if request.method == 'POST':
        if request.form:
            try:
                genre_title = request.form['genre_title']
                if(genre_title):
                    newGenre = Genre(title=genre_title)
                    db.session.add(newGenre)
                    db.session.commit()
                    flash(f"Genre {genre_title} has been added!",'success')
            except:
                flash("An error occured while adding the genre.",'error')
            return redirect(url_for('admin.manage_genres_page'))
        else:
            try:
                data = request.get_json()
                call_type = data['type']
                if call_type == 'add_new':
                    current_details = db.session.query(Genre).filter_by(id=int(data['genre_id'])).delete()
                    db.session.commit()
                    flash("Genre deleted successfully.",'success')
                elif call_type == 'update':
                    current_details = db.session.query(Genre).filter_by(id=int(data['genre_id'])).first()
                    current_details.title = data['new_title']
                    db.session.commit()
                    flash(f"Genre title successfully updated to {data['new_title']}.",'success')
                return jsonify({'status': 'success', 'value': 'Updated success'})
            except:
                flash("An error occured while deleting the genre.",'error')
                return jsonify({'status': 'success', 'value': 'Delete failed'})
    all_genre = Genre.query.order_by(desc(Genre.created)).all()
    context = {
        'user':current_user,
        'all_genre':all_genre,
        }
    return render_template('manage_genres.html', context=context)

####### Manage announcements
@admin.route('/dashboard/announcement/', methods=['GET', 'POST'])
@login_required
def manage_announcement_page():
    if not(is_allowed(current_user, allowed_roles=[1,])):
        flash('You are not authorized to manage users.', 'error')
        return redirect(url_for('admin.home_page'))
    if request.method == 'POST':
        if request.form:
            new_title = request.form['announce_title']
            new_content = request.form['announce_content']
            if new_content:
                try:
                    new_announce = Announcement(title=new_title, content=new_content)
                    db.session.add(new_announce)
                    db.session.commit()
                    flash("The announcement has been published.",'success')
                except:
                    flash("An error occured while adding the announcement.",'error')
                return redirect(url_for('admin.manage_announcement_page'))
        else:
            try:
                data = request.get_json()['announce_id']
                current_details = db.session.query(Announcement).filter_by(id=int(data)).delete()
                db.session.commit()
                flash("Announcement deleted successfully.",'success')
            except:
                flash("Announcement delete failed.",'error')
            return jsonify({'status': 'success', 'value': ''})
    all_announce = Announcement.query.order_by(desc(Announcement.created_date)).all()
    context = {
        'user':current_user,
        'all_announce':all_announce,
        }
    return render_template('manage_announcements.html', context=context) 

####### Manage announcements
@admin.route('/dashboard/reports/', methods=['GET', 'POST'])
@login_required
def manage_reports_page():
    if not(is_allowed(current_user, allowed_roles=[1,2])):
        flash('You are not authorized to manage users.', 'error')
        return redirect(url_for('admin.home_page'))
    if request.method == 'POST':
        try:
            data = request.get_json()
            call_type = data['type']
            report_id = data['report_id']
            if call_type == 'change':
                current_details = db.session.query(ReportBook).filter_by(id=int(report_id)).first()
                if(current_details.is_read):
                    current_details.is_read = 0
                else:
                    current_details.is_read = 1
                db.session.commit()
                flash("Report state changed successfully.",'success')
            elif call_type == 'delete':
                current_details = db.session.query(ReportBook).filter_by(id=int(report_id)).delete()
                db.session.commit()
                flash("Report deleted successfully.",'success')
        except:
            flash("Report state change failed.",'error')
        return jsonify({'status': 'success', 'value': ''})
    all_unread = ReportBook.query.filter_by(is_read=0).order_by(desc(ReportBook.created_date)).all()
    all_read = ReportBook.query.filter_by(is_read=1).order_by(desc(ReportBook.created_date)).all()
    context = {
        'user':current_user,
        'all_unread':all_unread,
        'all_read':all_read,
        }
    return render_template('reports.html', context=context) 

####### Manage announcements
@admin.route('/dashboard/newsletter/', methods=['GET', 'POST'])
@login_required
def newsletter_page():
    if not(is_allowed(current_user, allowed_roles=[1,])):
        flash('You are not authorized to manage users.', 'error')
        return redirect(url_for('admin.home_page'))
    if request.method == 'POST':
        if 'mail_content' in request.form:
            if request.form['mail_content']:
                all_subs = NewsLetterSubscription.query.all()
                recep_list = []
                for sub in all_subs:
                    recep_list.append(str(sub.email))
                if len(recep_list) > 500:
                    threads = list()
                    recep_list = [recep_list[i:i + 500] for i in range(0, len(recep_list), 500)]
                    for mail_list in recep_list:
                        thread = threading.Thread(target=send_custom_newsletter, args=(mail_list, request.form['mail_content']))
                        threads.append(thread)
                        thread.start()
                else:
                    thread = threading.Thread(target=send_custom_newsletter, args=(recep_list, request.form['mail_content']))
                    thread.start()
                flash("Newsletter sent to all subscribers.", "success")
            return redirect(url_for('admin.newsletter_page'))
        else:
            all_subs = NewsLetterSubscription.query.all()
            latest_books = Book.query.filter_by(is_approved=1).order_by(desc(Book.created)).limit(4).all()
            mail_cards = ""
            for book in latest_books:
                mail_cards += f"""
                <td class="column column-1" width="33.333333333333336%" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; font-weight: 400; text-align: left; vertical-align: top; border-top: 0px; border-right: 0px; border-bottom: 0px; border-left: 0px;">
					<table class="image_block block-2" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
						<tr>
							<td class="pad" style="width:100%;padding-right:0px;padding-left:0px;padding-top:5px;">
								<div class="alignment" align="center" style="line-height:10px"><img src="{request.url_root}webapp/static/uploads/{book.cover_img}" style="display: block; height: auto; border: 0; width: 200px; max-width: 100%;" width="200" alt="{book.title}" title="{book.title}"></div>
							</td>
						</tr>
					</table>
					<table class="text_block block-3" width="100%" border="0" cellpadding="10" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;">
						<tr>
							<td class="pad">
								<div style="font-family: sans-serif">
									<div class style="font-size: 12px; font-family: Arial, Helvetica Neue, Helvetica, sans-serif; mso-line-height-alt: 14.399999999999999px; color: #ffffff; line-height: 1.2;">
										<p style="margin: 0; font-size: 16px; text-align: center; mso-line-height-alt: 19.2px;"><em><strong>{book.title}</strong></em></p>
									</div>
								</div>
							</td>
						</tr>
					</table>
					<table class="text_block block-4" width="100%" border="0" cellpadding="10" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt; word-break: break-word;">
						<tr>
							<td class="pad">
								<div style="font-family: sans-serif">
									<div class style="font-size: 12px; font-family: Arial, Helvetica Neue, Helvetica, sans-serif; mso-line-height-alt: 14.399999999999999px; color: #ffffff; line-height: 1.2;">
										<p style="margin: 0; font-size: 14px; text-align: center; mso-line-height-alt: 16.8px;">{book.synopsis}</p>
									</div>
								</div>
							</td>
						</tr>
					</table>
					<table class="button_block block-5" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace: 0pt; mso-table-rspace: 0pt;">
						<tr>
							<td class="pad" style="padding-bottom:15px;padding-left:10px;padding-right:10px;padding-top:10px;text-align:center;">
								<div class="alignment" align="center">
									<!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="{request.url_root}book/{book.id}/" style="height:42px;width:115px;v-text-anchor:middle;" arcsize="10%" stroke="false" fillcolor="#46cdcf"><w:anchorlock/><v:textbox inset="0px,0px,0px,0px"><center style="color:#ffffff; font-family:Arial, sans-serif; font-size:16px"><![endif]--><a href="{request.url_root}book/{book.id}/" target="_blank" style="text-decoration:none;display:inline-block;color:#ffffff;background-color:#46cdcf;border-radius:4px;width:auto;border-top:0px solid transparent;font-weight:400;border-right:0px solid transparent;border-bottom:0px solid transparent;border-left:0px solid transparent;padding-top:5px;padding-bottom:5px;font-family:Arial, Helvetica Neue, Helvetica, sans-serif;font-size:16px;text-align:center;mso-border-alt:none;word-break:keep-all;"><span style="padding-left:20px;padding-right:20px;font-size:16px;display:inline-block;letter-spacing:normal;"><span dir="ltr" style="margin: 0; word-break: break-word; line-height: 32px;">View Book</span></span></a>
									<!--[if mso]></center></v:textbox></v:roundrect><![endif]-->
								</div>
							</td>
						</tr>
					</table>
                </td>
                """
            recep_list = []
            for sub in all_subs:
                recep_list.append(str(sub.email))
            if len(recep_list) > 500:
                threads = list()
                recep_list = [recep_list[i:i + 500] for i in range(0, len(recep_list), 500)]
                for mail_list in recep_list:
                    thread = threading.Thread(target=send_newsletter, args=(mail_list, mail_cards))
                    threads.append(thread)
                    thread.start()
            else:
                thread = threading.Thread(target=send_newsletter, args=(recep_list, mail_cards))
                thread.start()
            flash("Newsletter sent to all subscribers.", "success")
            return redirect(url_for('admin.newsletter_page'))
    context = {
        'user':current_user,
        }
    return render_template('newsletter.html', context=context)

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
        if(userQuery.is_banned == 0):
            login_user(userQuery)
            if userQuery.userlevel == 0:
                flash(f'Welcome back, {userQuery.username}.', 'success')
                return redirect(url_for('webapp.home_page'))
            elif userQuery.userlevel in [1, 2]:
                flash(f'Welcome back, {userQuery.username}.', 'success')
                return redirect(url_for('admin.dashboard_page'))
        else:
            flash("Your account has been banned due to suspicious activity.", 'error')
            return redirect(url_for('admin.home_page'))
    else:
        flash('This email is not a registered email. Please sign up first to use SSO.', 'error')
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
        flash(f'Welcome back, {userQuery.username}.', 'success')
        return redirect(url_for('admin.dashboard_page'))
    else:
        flash('This email is not a registered email. Please sign up first to use SSO.', 'error')
    return redirect(url_for('admin.home_page'))
