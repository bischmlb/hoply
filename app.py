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
            users = showUsers()
            content = showContent()
            time = showTimestamp()
            pid = showPostId()
            return render_template('content.html', list_users=users,
                                                    list_content=content,
                                                    list_timestamp = time,
                                                    list_pid = pid,
                                                    generateComments=showComments,
                                                    generateCommentsUser=showCommentsUser)
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
    users = showUsers()
    content = showContent()
    time = showTimestamp()
    pid = showPostId()
    return render_template('content.html', list_users=users,
                                           list_content=content,
                                           list_timestamp = time,
                                           list_pid = pid,
                                           generateComments=showComments,
                                           generateCommentsUser=showCommentsUser)

@app.route("/post", methods=['GET','POST'])
def post():
    user = session.get('user_id')
    if request.method == 'POST':
        content = request.form.get('content')
        create_post(gen(), user, content)
        print("nice :)")
        users = showUsers()
        content= showContent()
        time = showTimestamp()
        pid = showPostId()
    return render_template('content.html', list_users = users,
                                           list_content = content,
                                           list_timestamp = time,
                                           list_pid = pid,
                                           generateComments=showComments,
                                           generateCommentsUser=showCommentsUser)


@app.route("/comment", methods=['GET','POST'])
def comment():
    user = session.get('user_id')
    if request.method == 'POST':
        pid = request.form.get('pid')
        content = request.form.get('content')
        comment = add_comment(user, int(pid), content)
        return redirect(url_for('content'))




### --- helpers --- ###

def most_frequent(userid):
    List = post_iter(userid)
    #List=list(itertools.chain.from_iterable(List))
    print(List)
    occurence_count = Counter(List)
    print(occurence_count.most_common(1)[0][0])
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

def showUsers():
    list = fetch_postAll()
    total = []
    for x in list:
        total.append(x.user_id)
    return total

def showContent():
    list = fetch_postAll()
    total = []
    for x in list:
        total.append(x.content)
    return total

def showTimestamp():
    list = fetch_postAll()
    total = []
    for x in list:
        total.append(x.date_posted)
    return total

def showPostId():
    list = fetch_postAll()
    total = []
    for x in list:
        total.append(x.id)
    return total

def showComments(pid):
    list = Comment.query.filter_by(post_id = pid).all()
    total = []
    for x in list:
        total.append(x.content)
    return total

def showCommentsUser(pid):
    list = Comment.query.filter_by(post_id = pid).all()
    total = []
    for x in list:
        total.append(x.user_id)
    return total


app.jinja_env.globals.update(generateRandom=showComments)

def gen():
    rand = random.randint(1, 100000)
    constraint = Post.query.filter_by(id=rand).first()
    while rand == constraint:
        rand = random.randint(1, 3)
        if rand != constraint:
            return rand
    return rand

def fetch_postByUser(post_id):
    return Post.query.filter_by(id=post_id).all()

def fetch_postAll():
    return Post.query.order_by(Post.date_posted.desc()).all()

def create_post(post_id,user_id,content):
    new_post= Post(id=post_id,user_id=user_id,content=content, date_posted = datetime.utcnow().replace(tzinfo=simple_utc()).isoformat())
    db.session.add(new_post)
    db.session.commit()

def add_comment(user_id,post_id,content):
    new_comment = Comment(user_id=user_id,post_id=post_id,content=content, date_posted = datetime.utcnow().replace(tzinfo=simple_utc()).isoformat())
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
        new_user = User(id=new_id,username=new_username,date_posted=datetime.utcnow().replace(tzinfo=simple_utc()).isoformat())
        db.session.add(new_user)
        db.session.commit()
    else:
        print("Name is already taken")




if __name__ == '__main__':
    app.run(debug=True)
