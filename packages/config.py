import os

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQL_URI')
    JSON_SORT_KEYS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_ADDRESS')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')