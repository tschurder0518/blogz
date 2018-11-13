from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', methods=['POST', 'GET'])
def index():




    blogs = Blog.query.all()
    return render_template('blog.html',title="Build A Blog", 
        blogs=blogs)

#@app.route('/blog', defaults={'blog_id' : 'All'})
#@app.route('/blog/<blog_id>')# one of these two are working
#@app.route('/blog/<int:blog_id>')
#def blog(blog_id):
#   if blog_id != 'All':
#       blog = Blog.query.get(int(blog_id))
#       return render_template('single.html',title=blog.title,blog=blog)
#
#   blogs = Blog.query.all()
#   return render_template('blogs.html',title="Build-a-Blog",
#       blogs=blogs)

@app.route('/display', methods=['GET'])
def display():
    id = request.args.get("id")
    blog = Blog.query.filter_by(id=id).first()
    return render_template('single.html', title=blog.title,
        body=blog.body)

@app.route('/newpost', methods=['POST', 'GET'])
def add_post():
    if request.method == 'POST':
        entry_title = request.form['title']
        entry_body = request.form['body']
        if len(entry_title) == 0:
            flash("Please enter a title")
            return render_template('/newpost.html')
        if len(entry_body) == 0:
            flash("Please enter body")
            return render_template('/newpost.html')
        blog_entry = Blog(entry_title, entry_body)
        db.session.add(blog_entry)
        db.session.commit()
        return redirect('/display?id='+ str(blog_entry.id))
    else:
        return render_template('/newpost.html')



if __name__ == '__main__':
    app.run()