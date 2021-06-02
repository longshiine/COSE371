from datetime import timedelta
from flask import Flask, render_template, request, url_for, redirect, session, escape
import psycopg2

app = Flask(__name__)
app.secret_key = 'any random string'
connect = psycopg2.connect("dbname=qna user=postgres password=0108")
cur = connect.cursor()


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST': 
        id = request.form["id"]
        pw = request.form["pw"]
        btn = request.form["btn"]
        result = None
        cur.execute(f"select user_id, password, name, auth_code from users where user_id='{id}';")
        result = cur.fetchall()
        if len(result) == 0:
            # no result
            return "<script>alert('존재하지 않는 아이디입니다.');history.back();</script>"
        else:
            user_id = result[0][0]
            user_pw = result[0][1]
            auth = result[0][3]
            if user_pw == pw:
                session['userID'] = id
                session['userAuth'] = str(auth)
                return redirect(url_for("home"))
            else:
                return f"<script>alert('비밀번호가 일치하지 않습니다.');history.back();</script>"

@app.route('/logout') 
def logout(): 
    session.pop('userID', None) 
    return redirect(url_for('login'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    if request.method == 'POST':
        id = request.form["id"]
        name = request.form["name"]
        pw = request.form["pw"]
        re_pw = request.form["re_pw"]
        auth_value = request.form["auth"]
        auth_code = request.form['auth_code']
        btn = request.form["btn"]
        cur.execute(f"select user_id from users where user_id='{id}';")
        result = cur.fetchall()
        if len(result) != 0:
            return f"<script>alert('{id} - 동일한 아이디가 존재합니다.');history.back();</script>"
        else:
            if len(id)== 0 or len(pw) == 0:
                return f"<script>alert('아이디와 비밀번호는 비워둘 수 없습니다.');history.back();</script>"
            if len(name) == 0:
                return f"<script>alert('이름을 입력해주세요!');history.back();</script>"
            if len(name) > 20:
                return f"<script>alert('이름은 20자 미만입니다!');history.back();</script>"
            if pw != re_pw or len(re_pw) == 0:
                return f"<script>alert('비밀번호를 다시 확인해주세요.');history.back();</script>"
            if auth_code == "003":
                return f"<script>alert('교수님은 별도로 말씀해주시기 바랍니다...!');history.back();</script>"
            if auth_code == "002":
                if auth_value != "1234":
                    return f"<script>alert('인증코드가 잘못되었습니다!');history.back();</script>"
            cur.execute(f"insert into users values('{id}','{pw}','{name}','{auth_code}');")
            connect.commit()
            session['userID'] = id
            session['userAuth'] = str(auth_code)
            return f"<script>alert('계정가입이 완료되었습니다!!');location.href= 'home'</script>"

@app.route("/home", methods=["GET", "POST"])
def home():
    if 'userID' in session:
        cur.execute("select post_id, title, name, date, (select count(*) from post_comment where post_comment.post_id = post.post_id) as commentCnt, auth_code from post, users where post.user_id = users.user_id order by auth_code desc, post_id desc;")
        posts  = cur.fetchall()
        return render_template("main.html", posts = posts)
    return redirect(url_for("login"))

@app.route("/write", methods=["POST", "GET"])
def write():
    if 'userID' in session:
        if request.method == 'GET':
            return render_template("write.html")
        elif request.method == 'POST':
            cur.execute("select post_id from post order by post_id desc;")
            result = cur.fetchall()
            if len(result) != 0:
                post_id = (result[0][0]) + 1
            else:
                post_id = 1
            user_id = '%s' % escape(session['userID'])
            board_id = "자유질문"
            title = request.form["title"]
            content = request.form["content"] 
            btn = request.form["btn"]
            cur.execute(f"insert into post values('{post_id}', '자유질문', '{user_id}', now(), '{title}', '{content}')")
            connect.commit()
            cur.execute(f"insert into user_post values('{user_id}', '{post_id}')")
            connect.commit()
            return redirect(url_for("home"))
    return redirect(url_for("login"))

@app.route("/post/<post_id>", methods=["POST", "GET"])
def post(post_id):
    if 'userID' in session:
        if request.method == 'GET':
            cur.execute(f"select board_id, post_id, title, content, user_id, date, post_id from post where post_id = '{post_id}'")
            post = cur.fetchall()
            cur.execute(f"select comment_id, name, date, content, auth_code from post_comment natural join comment natural join users where post_id = '{post_id}'")
            comments = cur.fetchall()
            cur.execute(f"select count(comment_id) from post_comment where post_id = '{post_id}'")
            count = cur.fetchall()
            return render_template("post.html", post=post, comments=comments, count=count[0][0])
        elif request.method == 'POST':
            cur.execute(f"select comment_id from comment order by comment_id desc;")
            result = cur.fetchall()
            if len(result) != 0:
                comment_id = (result[0][0]) + 1
            else:
                comment_id = 1
            content = request.form["content"]
            user_id = '%s' % escape(session['userID'])
            cur.execute(f"insert into comment values('{comment_id}', '{post_id}', '{user_id}', now(), '{content}')")
            connect.commit()
            cur.execute(f"insert into post_comment values('{post_id}', '{comment_id}')")
            connect.commit()
            return redirect(url_for('post', post_id=post_id))
    return redirect(url_for("login"))

@app.route("/mypage", methods=["POST", "GET"])
def mypage():
    if 'userID' in session:
        if request.method == 'GET':
            user_id = '%s' % escape(session['userID'])
            cur.execute(f"select user_id, name, auth_code, type from users natural join auth where user_id = '{user_id}'")
            user = cur.fetchall()
            cur.execute(f"select board_id, post_id, title, content, user_id, date from post where user_id = '{user_id}'")
            posts = cur.fetchall()
            cur.execute(f"select comment_id, user_id, date, content from comment where user_id = '{user_id}'")
            comments = cur.fetchall()
            cur.execute(f"select count(post_id) from post where user_id = '{user_id}'")
            posts_count  = cur.fetchall()
            if len(posts_count) == 0:
                posts_count = 0
            else:
                posts_count = posts_count[0][0]
            cur.execute(f"select count(comment_id) from comment where user_id = '{user_id}'")
            comments_count = cur.fetchall()
            if len(comments_count) == 0:
                comments_count = 0
            else:
                comments_count = comments_count[0][0]
            return render_template("mypage.html", user=user, posts=posts, comments=comments, posts_count = posts_count,  comments_count = comments_count)
        #elif request.method == 'POST':
    return redirect(url_for("login"))

@app.route("/deletePost/<post_id>", methods=["GET","POST"])
def deletePost(post_id):
    if 'userID' in session:
        user_id = '%s' % escape(session['userID'])
        cur.execute(f"delete from post_comment where post_id = '{post_id}'")
        connect.commit()
        cur.execute(f"delete from comment where post_id = '{post_id}'")
        connect.commit()
        cur.execute(f"delete from user_post where post_id = '{post_id}'")
        connect.commit()
        cur.execute(f"delete from post where post_id = '{post_id}'")
        connect.commit()
        return redirect(url_for('mypage'))
    return redirect(url_for("login"))

@app.route("/editPost/<post_id>", methods=["POST", "GET"])
def editPost(post_id):
    if 'userID' in session:
        if request.method == 'GET':
            cur.execute(f"select post_id, title, content from post where post_id = '{post_id}'")
            post = cur.fetchall()
            return render_template("edit.html", post=post)
        elif request.method == 'POST':
            title = str(request.form["title"])
            content = str(request.form["content"])
            cur.execute(f"update post set title='{title}' where post_id = '{post_id}'")
            connect.commit()
            cur.execute(f"update post set content='{content}' where post_id = '{post_id}'")
            connect.commit()
            return redirect(url_for('mypage'))
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run()