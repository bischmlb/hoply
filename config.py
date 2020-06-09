import os
from datetime import datetime, tzinfo, timedelta,timezone
from flask import Flask, render_template, request, redirect, url_for, flash, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import requests
import base64
from collections import Counter
import itertools


def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SECRET_KEY'] = os.urandom(12)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
    if not os.path.exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    return app


app = create_app()
db = SQLAlchemy(app)


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
def aslocaltimestr(utc_dt):
    return utc_to_local(utc_dt).strftime('%Y-%m-%dT%H:%M:%S.' + '%f'.rstrip('0') + '+02:00')  ## rstrip required to make compatible with remote database and avoid duplicate entries, cause not recognized as UNIQUE

# print(aslocaltimestr(datetime.utcnow()))
# print(datetime.now())

class User(db.Model):
    id = db.Column(db.String(30), unique=True, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    date_posted = db.Column(db.String(32), nullable=False, default=aslocaltimestr(datetime.utcnow()))
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment',backref='commentor',lazy=True)
    def __repr__(self):
        return f"User('{self.id}',''{self.username}'','{self.date_posted}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(30), db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.String(32), nullable=False, default=aslocaltimestr(datetime.utcnow()))
    comments = db.relationship('Comment',backref='root',lazy=True)
    def __repr__(self):
        return f"Post('{self.id}','{self.content}', '{self.date_posted}')"

class Comment(db.Model):
    user_id = db.Column(db.String(30), db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.String(32), primary_key=True ,nullable=False, default=aslocaltimestr(datetime.utcnow()))

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
def post(input, table):
    url = 'http://caracal.imada.sdu.dk/app2020/'+ table
    headers = {'Authorization' : 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYXBwMjAyMCJ9.PZG35xIvP9vuxirBshLunzYADEpn68wPgDUqzGDd7ok'}
    requests.post(url, data=input, headers=headers)

#################################
#topfan
def most_frequent(userid):
    List = post_iter(userid)
    occurence_count = Counter(List)
    return occurence_count.most_common(1)[0][0]

def post_iter(userid):
    posts = Post.query.filter_by(user_id=userid).all()
    postid = []
    commentsUserId = []
    for i in posts:
        postid.append(i.id)
    if not postid:
        return None
    for x in postid:
        comments = Comment.query.filter_by(post_id=x)
        if comments != None:
            for y in comments:
                commentsUserId.append(y.user_id)
    return commentsUserId

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

def add_user(new_id,new_username, stamp=aslocaltimestr(datetime.utcnow())):
    stamp2 = aslocaltimestr(datetime.utcnow())
    if checkUser(new_id):
        new_user = User(id=new_id,username=new_username,date_posted=stamp2)
        db.session.add(new_user)
        db.session.commit()
        upload = {'id': new_user.id, 'name':new_user.username,'stamp': new_user.date_posted}
        # print(upload)
        post(upload, 'users')
        return True
    else:
        return False

def create_post(post_id,user_id,content, stamp=aslocaltimestr(datetime.utcnow())):
    stamp2 = aslocaltimestr(datetime.utcnow())
    if checkPosts(post_id):
        new_post= Post(id=post_id,user_id=user_id,content=content, date_posted=stamp2)
        db.session.add(new_post)
        db.session.commit()
        upload = {'id':new_post.id,'user_id':new_post.user_id,'content':new_post.content,'stamp' : new_post.date_posted}
        post(upload, 'posts')
        return True
    else:
        return False

def add_commentRemote(user_id,post_id,content, stamp):
    if checkComment(user_id,post_id,stamp):
        new_comment = Comment(user_id=user_id,post_id=post_id,content=content, date_posted=stamp)
        db.session.add(new_comment)
        db.session.commit()
        upload = {'user_id':new_comment.user_id,'post_id':new_comment.post_id,'content':new_comment.content,'stamp':new_comment.date_posted}
        post(upload,'comments')
        return True
    else:
        return False

def add_comment(user_id,post_id,content):
    stamp = aslocaltimestr(datetime.utcnow())
    if checkComment(user_id,post_id, stamp):
        new_comment = Comment(user_id=user_id,post_id=post_id,content=content, date_posted=stamp)
        db.session.add(new_comment)
        db.session.commit()
        postMaker = new_comment.root.user_id
        topfan = most_frequent(postMaker)
        upload = {'user_id':new_comment.user_id,'post_id':new_comment.post_id,'content':new_comment.content,'stamp':new_comment.date_posted}

        post(upload,'comments')
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
