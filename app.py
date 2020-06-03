from flask import Markup
from config import *
import random

@app.route("/")
@app.route("/index", methods=['GET','POST'])
def index():
    if request.method == 'POST':
        session['user_id'] = request.form.get('userid')
        user_id = session['user_id']
        query = User.query.filter_by(id=user_id).first()
        if query == None:
            userNotFound = "Username was not recognized"
            return render_template('index.html', message=userNotFound)
        elif user_id == query.id:
            print("Sucessfully logged in")
            return render_template('content.html')
        else:
            return render_template('index.html')
    return render_template('index.html')


@app.route("/signup", methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        user_id = request.form.get('userid')
        full_name = request.form.get('name')
        print(user_id)
        add_user(user_id, full_name)
        return redirect(url_for('index'))
    else:
        return render_template('signup.html')


@app.route("/content", methods=['GET','POST'])
def content():
    return render_template('content.html')

@app.route("/post", methods=['GET','POST'])
def post():
    user = session.get('user_id')
    if request.method == 'POST':
        content = request.form.get('content')
        create_post(gen(), user, content)
        print("nice :)")
    return render_template('content.html')



def gen():
    rand = random.randint(1, 100000)
    constraint = Post.query.filter_by(id=rand).first()
    while rand == constraint:
        rand = random.randint(1, 3)
        if rand != constraint:
            return rand
    return rand




### --- helpers --- ###
def fetch_postByUser(post_id):
    post = Post.query.filter_by(id=post_id)

def fetch_postAll():
    posts = Post.query.all()

def create_post(post_id,user_id,content):
    new_post= Post(id=post_id,user_id=user_id,content=content)
    db.session.add(new_post)
    db.session.commit()

def add_comment(user_id,post_id,content):
    new_comment = Comment(user_id=user_id,post_id=post_id,content=content)
    db.session.add(new_comment)
    db.session.commit()

def checkUser(new_id):
    exist = User.query.filter_by(id=new_id)
    if exist == []: # If exist is empty, username is not taken
        return True
    else:
        return False

def add_user(new_id,new_username):
    if checkUser(new_id):
        new_user = User(id=new_id,username=new_username)
        db.session.add(new_user)
        db.session.commit()
    else:
        print("Name is already taken")




if __name__ == '__main__':
    app.run(debug=True)
