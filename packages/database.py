from datetime import datetime, date, timedelta
from packages import db, login_manager
from flask import current_app
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import case
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(40), nullable=False, default='default.png') 
    password_hash = db.Column(db.String(120), nullable=False) 
    balance = db.Column(db.Float, default=0)
    expenses = db.Column(db.Float, default=0)
    transactions = db.relationship('Transactions', backref='User', lazy=True)
    # budget = db.relationship('Budgets', backref='User', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Transactions(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.String(60), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today())

    def __repr__(self):
        return f"Transactions('{self.user_id}', '{self.id}', '{self.amount}', '{self.type}', '{self.date}')"

class Budget(db.Model):
    __tablename__ = "budgets"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    amount_used = db.Column(db.Float, nullable=False, default=0.00)
    category = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.String(60), nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=date.today())
    end_date = db.Column(db.Date, nullable=False)
    
    @classmethod
    def delete_expired(cls):
        expired_limit = 30
        expired_date = date.today() - timedelta(days=expired_limit)
        cls.query.filter(cls.end_date <= expired_date).delete()
        db.session.commit()

    # Hybrid Property is not displayed as a column
    @hybrid_property
    def status(self):
        if date.today() > self.end_date:
            return "EXPIRED"
        elif self.amount < self.amount_used:
            return "OVERBUDGET"
        return "ONGOING"

    @status.expression
    def status(cls):
        return case([(date.today() > cls.end_date, "EXPIRED"), 
        (cls.amount < cls.amount_used, "OVERBUDGET")], else_="ONGOING")

    def __repr__(self):
        return f"Budget('{self.user_id}', '{self.id}', '{self.amount}', '{self.category}', '{self.start_date}', '{self.end_date}', '{self.status}')"

class DailyRecords(db.Model):
    __tablename__ = "income&expense"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today())

    def __repr__(self):
        return f"('{self.user_id}', '{self.id}', '{self.amount}', '{self.type}', '{self.date}')"

class InterestHistory(db.Model):
    __tablename__ = "interesthistory"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bank_name = db.Column(db.String, nullable=False,  default='Some Bank')
    initial_capital = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    final_capital = db.Column(db.Float, nullable=False)
    type = db.Column(db.String, nullable=False)
    period = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"('{self.user_id}', '{self.bank_name}' '{self.initial_capital}', '{self.interest_rate}', '{self.final_capital}', '{self.type}', '{self.period}')"
