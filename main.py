from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    users = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, user):
        self.title = title
        self.body = body
        self.user = user

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'list_blogs', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():
    #blogs = Blog.query.all()
    #users = User.query.filter_by(user=user_id).all()
    blogs = Blog.query.all() #filter_by(users=users)
    return render_template('blog.html',blogs=blogs)

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html',title="Blogz", 
        users=users)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        if password != user.password and user.password != "NoneType":
            flash('User password incorrect')
            return redirect('/login')
        if username != user.username:
            flash("Username does not exist")
            return redirect('/login')

    return render_template('login.html',title='Blogz')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verifypassword']

        username_error = ''
        password_error = ''

        #username validation
        if username == '':
            flash("Please enter a username")
            username = ''
            return redirect('/signup')
        if len(username) < 3:
            flash("Please enter a valid username")
            username = ''
            return redirect('/signup')

        #password validation
        if password == '':
            flash("Please enter a valid password")
            password = ''
            verify = ''
            return redirect('/signup')
        if password != verify:
            flash("Your passwords do not match, please enter matching passwords")
            password = ''
            verify = ''
            return redirect('/signup')
        if len(password) < 3:
            flash("Please enter a valid password")
            password = ''
            verify = ''  
            return redirect('/signup')     

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            flash("That username already exists")

    return render_template('signup.html')

@app.route('/display', methods=['GET'])
def display():
    id = request.args.get("id")
    blog = Blog.query.filter_by(id=id).first()
    return render_template('single.html', title=blog.title,
        body=blog.body, user=blog.user)

@app.route('/profile', methods=['GET'])
def profile():
    user = User.query.filter_by(username=(request.args.get("user"))).first()
    blogs = Blog.query.filter_by(users=user.id).all()
    return render_template('profile.html',blogs=blogs, user=user)

@app.route('/newpost', methods=['POST', 'GET'])
def add_post():
    if request.method == 'POST':
        entry_title = request.form['title']
        entry_body = request.form['body']
        user = User.query.filter_by(username=session['username']).first()
        if len(entry_title) == 0:
            flash("Please enter a title")
            return render_template('/newpost.html')
        if len(entry_body) == 0:
            flash("Please enter body")
            return render_template('/newpost.html')
        blog_entry = Blog(entry_title, entry_body, user)
        db.session.add(blog_entry)
        db.session.commit()
        return redirect('/display?id='+ str(blog_entry.id))
    else:
        return render_template('/newpost.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


if __name__ == '__main__':
    app.run()