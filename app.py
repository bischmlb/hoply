from flask import Markup,flash, request, redirect, url_for
from config import *
import random
from collections import Counter
import itertools
from werkzeug.utils import secure_filename
import os

@app.route("/")
@app.route("/index", methods=['GET','POST'])
def index():
    os.system("rm -rf uploads/*")
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
            if session.get('user_id') == None:
                return render_template('index.html')
            return render_template('content.html', list_users=users,
                                                    list_content=content,
                                                    list_timestamp = time,
                                                    list_pid = pid,
                                                    generateComments=showComments,
                                                    generateCommentsUser=showCommentsUser,
                                                    checkImg=checkIfImg,
                                                    getNewStr=splitter2,
                                                    getImageStr=splitter)
    else:
        return render_template('index.html')
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg','mp4'])
    if request.method == 'POST':


        if 'file' not in request.files:
            print("ERROR: File not found.")
            errMessage = "File not found!"
            return render_template('content.html', filename=errMessage)
        file = request.files['file']
        if file.filename == '':
            print("ERROR: A file has not been selected.")
            errMessage = "A file has not been selected!"
            return render_template('content.html', filename=errMessage)
        if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
            try:
                filename = secure_filename(file.filename)
                absPath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(absPath)
                print("INFO: ", filename, "was successfully uploaded.")
                newfilename = filename + " was successfully uploaded!"
                os.system("rm -rf upload/*")
                users = showUsers()
                content = showContent()
                time = showTimestamp()
                pid = showPostId()
                return render_template('content.html', filename=filename,
                                                        list_users=users,
                                                        list_content=content,
                                                        list_timestamp = time,
                                                        list_pid = pid,
                                                        generateComments=showComments,
                                                        generateCommentsUser=showCommentsUser,
                                                        checkImg=checkIfImg,
                                                        getNewStr=splitter2,
                                                        getImageStr=splitter)
            except:
                print("EXCEPT ERRIOROROR")
                return redirect(url_for('content'))
        else:
            print("ERROR: File not in '.csv' format.")
            return render_template('content.html')


@app.route("/signup", methods=['GET','POST'])
def signup():
    os.system("rm -rf uploads/*")
    updateLocal()
    if request.method == 'POST':
        user_id = request.form.get('userid')
        full_name = request.form.get('name')
        # print(user_id)
        newUser = add_user(user_id, full_name)
        if newUser == False:
            return render_template('signup.html', message = "ID already taken")
        else:
            return redirect(url_for('index'))
    else:
        return render_template('signup.html')


@app.route("/content", methods=['GET','POST'])
def content():
    os.system("rm -rf uploads/*")
    if session.get('user_id') == None:
        return render_template('index.html')
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
                                           generateCommentsUser=showCommentsUser,
                                           checkImg=checkIfImg,
                                           getNewStr=splitter2,
                                           getImageStr=splitter)

@app.route("/post", methods=['GET','POST'])
def post():
    os.system("rm -rf uploads/*")
    updateLocal()
    user = session.get('user_id')
    if request.method == 'POST':
        content = request.form.get('content')
        imgStr = appendImg()
        contentImg = content + imgStr
        if contentImg == "": ## cannot make posts with no content
            return redirect(url_for("content"))
        create_post(gen(), user, contentImg)
        # print("nice :)")
        users = showUsers()
        content= showContent()
        time = showTimestamp()
        pid = showPostId()
    return render_template('content.html', list_users = users,
                                           list_content = content,
                                           list_timestamp = time,
                                           list_pid = pid,
                                           generateComments=showComments,
                                           generateCommentsUser=showCommentsUser,
                                           checkImg=checkIfImg,
                                           getNewStr=splitter2,
                                           getImageStr=splitter)


@app.route("/comment", methods=['GET','POST'])
def comment():
    os.system("rmdir uploads/*")
    updateLocal()
    user = session.get('user_id')
    if request.method == 'POST':
        pid = request.form.get('pid')
        content = request.form.get('content')

        comment = add_comment(user, int(pid), content)

        return redirect(url_for('content'))






### --- helpers --- ###
def convertImg(image_path):
    print("from convertImg", (image_path))
    with open(image_path, "rb") as img_file:
        print("open file, convert")
        converted = base64.b64encode(img_file.read()).decode('utf-8')
        # print("converted: ", converted)
        return "@IMG[" + converted + "]"

def appendImg():
    str = ""
    directory = os.path.join('uploads')
    for root,dirs,files in os.walk(directory):
        for file in files:
            print("from findFiles", file)
            print(convertImg("uploads/" + file) + "\n" + "hagsadgagdssagdagd")
            str = convertImg("uploads/" + file)
    return str

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions

def checkIfImg(str):
    if "@IMG[" in str:
        return True
    else:
        return False

def splitter2(str):
    splitAt = str.split("@")[0]
    return splitAt

def splitter(str):
    splitAt = str.split("@")[1]
    splitFirstBracket = splitAt.split("[")[1]
    splitFinal = splitFirstBracket.split("]")[0]
    return splitFinal


def most_frequent(userid):
    List = post_iter(userid)
    occurence_count = Counter(List)

    if not occurence_count:
        return False
    elif (occurence_count.most_common(1)[0][0] == userid and len(occurence_count) > 1):
        # if (occurence_count.most_common(1)[0][0] == userid && len(occurence_count)>1)
        return occurence_count.most_common(2)[1][0]
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
    commentlist = Comment.query.filter_by(post_id = pid).order_by(Comment.date_posted.asc()).all()
    total = []
    for x in commentlist:
        total.append(x.content)
    return total

def showCommentsUser(pid):
    showCommentlist = Comment.query.filter_by(post_id = pid).order_by(Comment.date_posted.asc()).all()
    total = []
    postOwner = Post.query.filter_by(id = pid).first().user_id
    topfan = most_frequent(postOwner)
    for x in showCommentlist:
        # print("x: ", x.user_id, "\t topfan: ", topfan)
        if x.user_id == topfan:
            total.append("⭐ " + x.user_id)
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
