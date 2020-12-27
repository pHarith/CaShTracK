from flask_wtf import FlaskForm
from wtforms import StringField as str_field, PasswordField as pwd_field, SubmitField as smt_field, BooleanField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email, Length, EqualTo, optional, ValidationError
from packages.database import User
from sqlalchemy import or_
from werkzeug.security import check_password_hash
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = str_field('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = str_field('Email', validators=[DataRequired(), Email()])
    password = pwd_field('Password', validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = pwd_field('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = smt_field('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken. Please choose a different one or log in instead.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email belongs to an existing user. Please choose a different one or log in instead.')


class LogInForm(FlaskForm):
    field = str_field(validators=[DataRequired(), Length(min=2, max=60)])
    password = pwd_field('Password', validators=[DataRequired(), Length(min=6, max=20)])
    remember = BooleanField('Remember Me')
    submit = smt_field('Log In')

    def validate_field(self, field):
        user = User.query.filter(or_(User.username==field.data, User.email==field.data)).first()
        if not user:
            return False
        else:
            return True


class AccountUpdateForm(FlaskForm):
    username = str_field('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = str_field('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = smt_field('Update Account')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username is already taken. Please choose a different one or log in instead.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email belongs to an existing user. Please choose a different one or log in instead.')


class PassWordChangeForm(FlaskForm):
    old_password = pwd_field('Old Password', validators=[DataRequired(), Length(min=6, max=20)])
    new_password = pwd_field('New Password', validators=[DataRequired(), Length(min=6, max=20)])
    confirm_new_password = pwd_field('Confirm New Password', validators=[DataRequired(), EqualTo('new_password', message='New Passwords must match.')])
    submit = smt_field('Change Password')

    def validate_old_password(self, old_password):
        if check_password_hash(current_user.password_hash, old_password.data):
            return True
        else:
            raise ValidationError('This Password does not belong to any user.')
            return False

    def validate_new_password(self, new_password):
        if self.old_password.data == self.new_password.data:
            raise ValidationError('Your New Password cannot match your Old Password.')
            return False
        else:
            return True
