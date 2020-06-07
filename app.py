from flask import Markup
from config import *
import random
from collections import Counter
import itertools

@app.route("/")
@app.route("/index", methods=['GET','POST'])
def index():
    updateLocal()
    if request.method == 'POST':
        ### --- Local --- ###
        session['user_id'] = request.form.get('userid')
        user_id = session['user_id']
        query = User.query.filter_by(id=user_id).first()
        if query == None:
            userNotFound = "Username was not recognized"
            return render_template('index.html', message=userNotFound)
        else: ### If lists are not empty it means user exists and we log in
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
    updateLocal()
    if request.method == 'POST':
        user_id = request.form.get('userid')
        full_name = request.form.get('name')
        print(user_id)
        newUser = add_user(user_id, full_name)
        if newUser == False:
            return render_template('signup.html', message = "ID already taken")
        else:
            return redirect(url_for('index'))
    else:
        return render_template('signup.html')


@app.route("/content", methods=['GET','POST'])
def content():
    updateLocal()
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
    updateLocal()
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
    updateLocal()
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
    # print(List)
    occurence_count = Counter(List)
    # print(occurence_count.most_common(1)[0][0])

    # print((userid,"'s Top Fan is: ",(occurence_count)))

    if not occurence_count:
        return False
    else:
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
    userlist = fetch_postAll()
    remoteList = []
    for x in postsJson:
        remoteList.append(x['user_id'])
    total = []
    for x in userlist:
        total.append(x.user_id)
    # print("\n\n\n\n",list(set(total + remoteList)))
    final = (total + remoteList)
    return final



def showContent():
    contentlist = fetch_postAll()
    remoteList = []
    for x in postsJson:
        remoteList.append(x['content'])
    total = []
    for x in contentlist:
        total.append(x.content)
    return (total + remoteList)

def showTimestamp():
    timestamplist = fetch_postAll()
    remoteList = []
    for x in postsJson:
        remoteList.append(x['stamp'])
    total = []
    for x in timestamplist:
        total.append(x.date_posted)
    return (total + remoteList)

def showPostId():
    postlist = fetch_postAll()
    remoteList = []
    for x in postsJson:
        remoteList.append(x['id'])
    total = []
    for x in postlist:
        total.append(x.id)
    return (total + remoteList)

def showComments(pid):
    commentlist = Comment.query.filter_by(post_id = pid).all()
    total = []
    for x in commentlist:
        total.append(x.content)
    return total

def showCommentsUser(pid):
    showCommentlist = Comment.query.filter_by(post_id = pid).all()
    total = []
    postOwner = Post.query.filter_by(id = pid).first().user_id
    topfan = most_frequent(postOwner)
    for x in showCommentlist:
        print("x: ", x.user_id, "\t topfan: ", topfan)
        if x.user_id == topfan:
            total.append("⭐ " + x.user_id)
        # elif:
        #     total.append(x.user_id)
        else:
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



def checkPosts(new_id):
    exist = Post.query.filter_by(id=new_id).first()
    if exist == None: # If exist is empty, username is avialable
        return True
    else:
        return False
'''
def checkComment(user_id,post_id,new_timestamp):
    #comments = Comment.query.filter_by(id=new_timestamp).all()
    #for i in comments:
        if (i.commentor.id==user_id && i.root.id==post_id)
            return False
    return True


    if existUser == None: # If exist is empty, username is avialable
        return True
    else:
        return False
'''






if __name__ == '__main__':
    app.run(debug=True)
