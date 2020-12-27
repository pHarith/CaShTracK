from flask import render_template as rnd_tmp, url_for, request, redirect, flash, Blueprint
from packages import db
from packages.users.helpers import save_picture
from packages.users.forms import (RegistrationForm, LogInForm, AccountUpdateForm, 
                                    PassWordChangeForm)
from packages.database import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from sqlalchemy import or_

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    """Register new users into the site"""
    # Redirect to dashboard if logged in
    if current_user.is_authenticated:
        return redirect(url_for('cashtrack.overview'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pwd = generate_password_hash(form.password.data)
        user = User(username = form.username.data, email = form.email.data, password_hash=hashed_pwd)
        db.session.add(user)
        db.session.commit()
        flash(f'Account Created for {request.form.get("username")}! Please Log In.', 'success')
        return redirect(url_for('users.login'))
    return rnd_tmp("register.html", form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    """Log users into their account"""
    # Redirect to dashboard if logged in
    if current_user.is_authenticated:
        return redirect(url_for('cashtrack.overview'))
    form = LogInForm()
    if form.validate_on_submit():
        user = User.query.filter(or_(User.username==form.field.data, User.email==form.field.data)).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Welcome, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('cashtrack.overview'))
        else:
            flash('Login Unsuccessful. Please check username/email or password!', 'danger')
    return rnd_tmp("login.html", form=form)


@users.route("/logout")
@login_required
def logout():
    """Log out the User back to Homepage"""
    logout_user()
    flash('You have logged out.', 'success')
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    """ Allows User to update account profile """
    form = AccountUpdateForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account Details Updated', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='/profile_pics/' + current_user.image_file)
    return rnd_tmp('account.html', image_file=image_file, form=form) 


@users.route("/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    """" Change user password """
    form = PassWordChangeForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.old_password.data):
            current_user.password_hash = generate_password_hash(str(form.new_password.data))
            db.session.commit()
            flash('Your Password has been updated', 'success')
            return redirect(url_for('users.account')) 
    return rnd_tmp("change.html", form=form)