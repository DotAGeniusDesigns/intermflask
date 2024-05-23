from flask import Flask, render_template, redirect, session, flash, request, url_for
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///projectlogin'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'

connect_db(app)
bcrypt = Bcrypt(app)

@app.route('/')
def home():
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        
        user = User(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        db.session.add(user)
        db.session.commit()

        session['username'] = user.username
        return redirect('/secret')

    return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['username'] = user.username
            return redirect('/secret')
        else:
            flash("Invalid credentials", 'danger')

    return render_template('login.html', form=form)

@app.route('/secret')
def secret():
    if 'username' not in session:
        flash("You must be logged in to view this page", 'danger')
        return redirect('/login')
    
    return render_template('secret.html')

@app.route('/logout')
def logout():
    session.pop('username')
    flash("You have been logged out", 'success')
    return redirect('/')

@app.route('/users/<username>')
def user_profile(username):
    if 'username' not in session or session['username'] != username:
        flash("You must be logged in to view this page", 'danger')
        return redirect('/login')

    user = User.query.get_or_404(username)
    return render_template('user_profile.html', user=user)

@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def add_feedback(username):
    if 'username' not in session or session['username'] != username:
        flash("You must be logged in to add feedback", 'danger')
        return redirect('/login')

    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        db.session.commit()

        return redirect(url_for('user_profile', username=username))

    return render_template('add_feedback.html', form=form)

@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)

    if 'username' not in session or session['username'] != feedback.username:
        flash("You must be logged in to edit feedback", 'danger')
        return redirect('/login')

    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()
        return redirect(url_for('user_profile', username=feedback.username))

    return render_template('edit_feedback.html', form=form)

@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)

    if 'username' not in session or session['username'] != feedback.username:
        flash("You must be logged in to delete feedback", 'danger')
        return redirect('/login')

    db.session.delete(feedback)
    db.session.commit()

    return redirect(url_for('user_profile', username=feedback.username))

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    if 'username' not in session or session['username'] != username:
        flash("You must be logged in to delete your account", 'danger')
        return redirect('/login')

    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username')

    return redirect('/')
