

from flask import Blueprint, render_template


home_app = Blueprint(
    'home_app', __name__, root_path='/', template_folder='templates')


@home_app.route('/')
def home():
    """
    """
    return render_template("index.html")


@home_app.route('/about/howto.html')
def howto():
    # todo(): delete
    return render_template("about/howto.html")
