from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:!!MyBl0gPass!!@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    posts = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.pw_hash = make_pw_hash(password)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'static']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['email'] = email
            flash("Logged in", 'info')
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            flash("The email <strong>{0}</strong> is already registered".format(email), 'danger')

    return render_template('register.html')


@app.route('/logout', methods=['POST'])
def logout():
    del session['email']
    return redirect('/')


@app.route('/', methods=['POST', 'GET'])
def index():

     owner = User.query.filter_by(email=session['email']).first()
     posts = Blog.query.filter_by(owner=owner).all()
     return render_template('posts.html', title="Build-a-Blog!", posts=posts)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(email=session['email']).first()
    
    if request.method == 'POST':
        post_title = request.form['title']
        post_body = request.form['body']
        if not not_empty(post_title):
            flash('Please enter a title')
            return redirect('/newpost')
        if not not_empty(post_body):
            flash('Please enter some text in the body')
            return redirect('/newpost')
        new_post = Blog(post_title, post_body, owner)
        db.session.add(new_post)
        db.session.commit()
        id = new_post.id
        url = 'blog?id=' + str(id)
        return redirect(url)
        

    posts = Blog.query.filter_by(owner=owner).all()
    return render_template('newpost.html', title="Posts!",
                           posts=posts)
def not_empty(string):
    if string == '':
        return False
    else:
        return True


@app.route('/blog', methods=['GET'])
def blog():
    owner = User.query.filter_by(email=session['email']).first()
    posts = Blog.query.filter_by(owner=owner).all()
    if request.args:
        id = request.args.get('id', type=int)
        post = Blog.query.get(id)
        return render_template('blog.html',title=post.title, post=post)
    
    
    # if not_empty(id):
    #     post = posts[id]
    #     return render_template('blog.html', title=post.title, post=post)
    
    return render_template('posts.html', title="Posts!",
                           posts=posts)

@app.route('/delete-task', methods=['POST'])
def delete_task():

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()