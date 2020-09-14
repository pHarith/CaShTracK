from flask import Blueprint, url_for, render_template as rnd_tmp, redirect
from flask_login import current_user

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('cashtrack.overview'))
    return rnd_tmp("home.html")

