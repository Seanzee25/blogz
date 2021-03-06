from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+pymysql://blogz:beproductive@localhost:8889/blogz")
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
app.secret_key = "y338wpoie93844"


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    body = db.Column(db.String(500))
    pub_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship('Likes', backref='blog')

    def __init__(self, title, body, user, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.user = user
        self.pub_date = pub_date


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(40))
    email = db.Column(db.String(120))
    pw_hash = db.Column(db.String(120))
    create_date = db.Column(db.DateTime)
    posts = db.relationship('Blog', backref="user")
    liked = db.relationship('Likes', backref='liked_by', foreign_keys="Likes.liked_by_id")
    likes = db.relationship('Likes', backref='user', foreign_keys="Likes.user_id")

    def __init__(self, user_name, email, password):
        self.user_name = user_name
        self.email = email
        self.pw_hash = make_pw_hash(password)
        self.create_date = datetime.utcnow()


class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    liked_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog, user, liked_by):
        self.blog = blog
        self.user = user
        self.liked_by = liked_by


@app.before_request
def require_login():
    allowed_route = ["login", "signup", "index", "displayAllEntries"]
    if request.endpoint not in allowed_route and 'email' not in session:
        return redirect("/login")


def get_users():
    return User.query.all()


@app.route("/")
def index():
    return render_template("index.html", users=get_users())


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_pw_hash(password, user.pw_hash):
            session["email"] = email
            session["username"] = user.user_name
            session["id"] = user.id
            return redirect("/")
        else:
            return render_template("login.html",
                                   error="Email or password incorrect")

    return render_template("login.html")


def validate_username_password(string):
    if len(string) == 0:
        return "Required"
    if not re.fullmatch('^.{3,20}$', string):
        return "Must be within character limit (3-20)."
    if re.search(r'\s', string):
        return "Spaces not allowed"
    return ''


def validate_password_verify(password, password_verify):
    if password != password_verify:
        return "Passwords do not match."
    return ''


def validate_email(email):
    if(len(email) == 0):
        return "Required"
    if re.search(r'\s', email):
        return "Spaces not allowed"
    # if not re.fullmatch('^.{3,20}$', email):
    #     return "Must be within character limit (3-20)."
    if len(email) > 0 and not re.fullmatch(r'^[^@.]+@[^@.]+\.[^@.]+$', email):
        return "Invalid email"
    return ''


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if(request.method == "POST"):
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["pwd"]
        password_verify = request.form["verify-pwd"]

        username_error = validate_username_password(username)
        password_error = validate_username_password(password)
        password_verify_error = validate_password_verify(password,
                                                         password_verify)
        email_error = validate_email(email)

        if not username_error and (User.query
                                   .filter_by(user_name=username)
                                   .first()):
            username_error = "Username already exists"
        if not email_error and User.query.filter_by(email=email).first():
            email_error = "User with that email already exists"

        if (not username_error and not password_error
                and not password_verify_error and not email_error):
            user = User(username, email, password)
            db.session.add(user)
            db.session.commit()
            session["email"] = email
            session["username"] = username
            session["id"] = user.id
            return redirect('/newpost')

        return render_template("signup.html",
                               username=username, email=email,
                               username_error=username_error,
                               password_error=password_error,
                               password_verify_error=password_verify_error,
                               email_error=email_error)
    else:
        return render_template("signup.html")


@app.route('/logout')
def logout():
    del session["email"]
    del session["username"]
    del session["id"]
    return redirect("./blog")


@app.route('/blog')
def displayAllEntries():
    blog_id = request.args.get("id")
    user_id = request.args.get("user_id")

    if(user_id is not None):
        user = User.query.get(user_id)
        return render_template("singleUser.html", user=user, blogs=user.posts)
    elif(blog_id is not None):
        blog_entry = Blog.query.get(blog_id)
        like = Likes.query.filter_by(blog_id=blog_id, liked_by_id=session["id"]).first()
        liked = True if like else False
        return render_template("entry.html", blog=blog_entry, liked=liked)
    else:
        blogs = Blog.query.order_by(db.desc(Blog.pub_date)).all()
        return render_template("blog.html", blogs=blogs)


@app.route('/like')
def like():
    blog_id = request.args.get("blog_id")
    user_id = request.args.get("user_id")

    blog = Blog.query.get(blog_id)
    liked_by = User.query.get(user_id)
    user = blog.user

    if(request.args.get("like") == "true"):
        blog_id = request.args.get("blog_id")
        user_id = request.args.get("user_id")

        blog = Blog.query.get(blog_id)
        liked_by = User.query.get(user_id)
        user = blog.user

        if(blog.user.id != liked_by.id):
            like = Likes(blog, user, liked_by)
            db.session.add(like)
            db.session.commit()
        return redirect("./blog?id={0}".format(blog_id))
    else:
        like = Likes.query.filter_by(blog_id=blog_id, liked_by_id=user_id).first()
        if like:
            db.session.delete(like)
            db.session.commit()
        return redirect("./blog?id={0}".format(blog_id))


@app.route('/newpost', methods=["POST", "GET"])
def createPost():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]

        title_error = ""
        body_error = ""

        if(not title):
            title_error = "Please fill in the title"
        if(not body):
            body_error = "Please fill in the body"
        if(len(body) > 500):
            body_error = "Limit to 500 characters"
        if(len(title) > 20):
            title_error = "Limit to 20 characters"
        if(title_error or body_error):
            return render_template("newpost.html", title_error=title_error,
                                   body_error=body_error, title=title, body=body)
        else:
            user = User.query.filter_by(email=session["email"]).first()
            blog = Blog(title, body, user)
            db.session.add(blog)
            db.session.commit()
            return redirect("./blog?id={0}".format(blog.id))
    else:
        return render_template("newpost.html")


if __name__ == "__main__":
    app.run()
