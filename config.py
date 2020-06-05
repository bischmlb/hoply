import os
from datetime import datetime, tzinfo, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import requests


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
    id = db.Column(db.String(20), unique=True, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    date_posted = db.Column(db.String(30), nullable=False, default=datetime.utcnow().replace(tzinfo=simple_utc()).isoformat())
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment',backref='commentor',lazy=True)
    def __repr__(self):
        return f"User('{self.username}','{self.date_posted}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.String(30), nullable=False, default=datetime.utcnow().replace(tzinfo=simple_utc()).isoformat())
    comments = db.relationship('Comment',backref='root',lazy=True)
    def __repr__(self):
        return f"Post('{self.id}','{self.content}', '{self.date_posted}')"

class Comment(db.Model):
    user_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.String(30), primary_key=True ,nullable=False, default=datetime.utcnow().replace(tzinfo=simple_utc()).isoformat())

    def __repr__(self):
        return f"Comment('{self.content}', '{self.date_posted}')"

db.create_all()

### requests remote database ###
remotePosts = requests.get('http://caracal.imada.sdu.dk/app2020/posts')
postsJson = remotePosts.json()
##
remoteUsers = requests.get('http://caracal.imada.sdu.dk/app2020/users')
usersJson = remoteUsers.json()
##
remoteComments = requests.get('http://caracal.imada.sdu.dk/app2020/comments')
commentsJson = remoteComments.json()
#################################


########## add to database methods #####
def checkUser(new_id):
    exist = User.query.filter_by(id=new_id).first()
    if exist == None: # If exist is empty, username is avialable
        return True
    else:
        return False
def checkPosts(new_id):
    exist = Post.query.filter_by(id=new_id).first()
    if exist == None: # If exist is empty, username is avialable
        return True
    else:
        return False
def checkComment(user_id,post_id,new_timestamp):
    comments = Comment.query.filter_by(date_posted=new_timestamp).all()
    for i in comments:
        if (i.commentor.id==user_id and i.root.id==post_id):
            return False
    return True

def add_user(new_id,new_username, stamp=datetime.utcnow().replace(tzinfo=simple_utc()).isoformat()):
    if checkUser(new_id):
        new_user = User(id=new_id,username=new_username,date_posted=stamp)
        db.session.add(new_user)
        db.session.commit()
        return True
    else:
        return False

def create_post(post_id,user_id,content, stamp=datetime.utcnow().replace(tzinfo=simple_utc()).isoformat()):
    if checkPosts(post_id):
        new_post= Post(id=post_id,user_id=user_id,content=content, date_posted=stamp)
        db.session.add(new_post)
        db.session.commit()
        return True
    else:
        return False

def add_commentRemote(user_id,post_id,content, stamp):
    if checkComment(user_id,post_id,stamp):
        new_comment = Comment(user_id=user_id,post_id=post_id,content=content, date_posted=stamp)
        db.session.add(new_comment)
        db.session.commit()
        return True
    else:
        return False

def add_comment(user_id,post_id,content):
    stamp = datetime.utcnow().replace(tzinfo=simple_utc()).isoformat()
    if checkComment(user_id,post_id, stamp):
        new_comment = Comment(user_id=user_id,post_id=post_id,content=content, date_posted=stamp)
        db.session.add(new_comment)
        db.session.commit()
        return True
    else:
        return False

###################################################
### methods for updating database ###
def updateUsers():
    for i in usersJson:
        id = i['id']
        name = i['name']
        timestamp = i['stamp']
        add_user(id,name,timestamp)

def updatePosts():
    for i in postsJson:
        id = i['id']
        user_id = i['user_id']
        content = i['content']
        timestamp = i['stamp']
        create_post(id,user_id,content,timestamp)

def updateComments():
    for i in commentsJson:
        user_id = i['user_id']
        post_id = i['post_id']
        content = i['content']
        timestamp = i['stamp']
        add_commentRemote(user_id, post_id, content, timestamp)


def updateLocal():
    try:
        updateUsers()
    except:
        print("Users table is already up to date")
    try:
        updatePosts()
    except:
        print("Posts table is already up to date")
    updateComments()

############################################################################ Helper for UTC format
### update database ###
updateLocal()       ###
#######################


########################################################################## Database structure
