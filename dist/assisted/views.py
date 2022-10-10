from flask import Blueprint,render_template, redirect


assisted = Blueprint('assisted', __name__, static_folder="static", static_url_path='/assisted/static' , template_folder='templates')


@assisted.route("/", methods=['GET', 'POST'])
@assisted.route("/home", methods=['GET', 'POST'])
def home_page():
  context = {}
  return render_template('asst-home.html', context=context)