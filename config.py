import os
from datetime import datetime, tzinfo, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename


def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SECRET_KEY'] = os.urandom(12)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    return app

app = create_app()
db = SQLAlchemy(app)

class simple_utc(tzinfo):
    def tzname(self,**kwargs):
        return "UTC"
    def utcoffset(self, dt):
        return timedelta(hours=2)
print(datetime.utcnow().replace(tzinfo=simple_utc()))
class User(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    date_posted = db.Column(db.String(30), nullable=False, default=datetime.utcnow().replace(tzinfo=simple_utc()).isoformat())
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.date_posted}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Post('{self.id}', '{self.date_posted}')"
