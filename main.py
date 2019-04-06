from flask import Flask, request, render_template, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+pymysql://build-a-blog:beproductive@localhost:8889/build-a-blog")
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
app.secret_key = "yapre093$##092#"


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, body, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date


@app.route('/blog')
def displayAllEntries():
    blog_id = request.args.get("id")

    if(blog_id is None):
        blogs = Blog.query.order_by(db.desc(Blog.pub_date)).all()
        return render_template("blog.html", blogs=blogs)
    else:
        blog_entry = Blog.query.filter_by(id=blog_id).first()
        return render_template("entry.html", blog=blog_entry)


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
        if(title_error or body_error):
            return render_template("newpost.html", title_error=title_error,
                                   body_error=body_error)
        else:
            blog = Blog(title, body)
            db.session.add(blog)
            db.session.commit()
            return redirect("./blog?id={0}".format(blog.id))
    else:
        return render_template("newpost.html")


if __name__ == "__main__":
    app.run()
