from flask import Flask, request, render_template, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+pymysql://build-a-blog:beproductive@localhost:8889/build-a-blog")
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
app.secret_key = "yapre093$##092#"

@app.route('/')
def index():
    return "Hello World!"

app.run()