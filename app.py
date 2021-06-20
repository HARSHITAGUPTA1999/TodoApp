from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import LengthRequired
from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, InputRequired, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
#from sqlalchemy.orm import sessionmaker
app = Flask(__name__)

# initlaising sql alchemy to set up a conenction
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ebfe4b13a1988c737131dfac'

# creating instance of the class SQLAlcmhey imported
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'
login_manager.login_message_category = "info"

# database is created using models which are created using classes


class LoginForm(FlaskForm):

    username = StringField(label='UserName', validators=[
                           InputRequired(), Length(min=2, max=30)])
    password = PasswordField(label='Password', validators=[
                             Length(min=2, max=80), InputRequired()])
    submit = SubmitField(label='Login')


class RegisterForm(FlaskForm):

    username = StringField(label='UserName', validators=[
                           InputRequired(), Length(min=2, max=30)])
    email_address = StringField(label='Email Address', validators=[
                                InputRequired(), Email(message="invalid email")])
    password1 = PasswordField(label='Password', validators=[
                              Length(min=2, max=80), InputRequired()])
    submit = SubmitField(label='Create Account')


class AddItemForm(FlaskForm):

    add_item = StringField(label='Task', validators=[
                           InputRequired(), Length(min=2, max=30)])
    add_desc = StringField(label='Description', validators=[
                           Length(min=2, max=80), InputRequired()])
    submit = SubmitField(label='Add')


class EditItemForm(FlaskForm):

    edit_item = StringField(label='Task', validators=[
                            InputRequired(), Length(min=2, max=30)])
    edit_desc = StringField(label='Description', validators=[
                            Length(min=2, max=80), InputRequired()])
    submit = SubmitField(label='Update')


# this table is not to be used anywhere in the code
# class User(UserMixin, db.Model):
#     user_id = db.Column(db.Integer(), primary_key=True)
#     username = db.Column(db.String(length=30), nullable=False)
#     email_address = db.Column(db.String(length=50), nullable=False, unique=True)
#     password_hash = db.Column(db.String(length=80), nullable=False)
#     items = db.relationship('Task', backref='owned_user', lazy=True)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False)
    email_address = db.Column(db.String(length=50),
                              nullable=False, unique=True)
    password_hash = db.Column(db.String(length=80), nullable=False)
    items = db.relationship('Task', backref='owned_user', lazy=True)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Task(db.Model):

    task_id = db.Column(db.Integer(), primary_key=True)
    task_title = db.Column(db.String(length=80), nullable=False)
    task_desc = db.Column(db.String(length=80), nullable=False)
    date_created = db.Column(db.Date, default=date.today())
    owner = db.Column(db.Integer(), db.ForeignKey('users.id'))

    def __repr__(self):
        return f"{self.task_title}"


@app.route('/')
@app.route('/home')
def home_page():
    return render_template("home.html")


@app.route('/about')
def about_page():
    return render_template("about.html")


@app.route('/mylist', methods=['GET', 'POST'])
@login_required
def mylist_page():

    form = AddItemForm()
    if request.method == "POST":

        new_task = Task(task_title=form.add_item.data,
                        task_desc=form.add_desc.data, owner=current_user.id)
        # print(new_task.task_title)
        # print(new_task.owner)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('mylist_page'))

    items = Task.query.filter_by(owner=current_user.id)
    return render_template("mylist.html", form=form, item=items)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password1.data, method='sha256')
        new_user = Users(username=form.username.data,
                         email_address=form.email_address.data,
                         password_hash=hashed_password)

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login_page'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)

                return redirect(url_for('mylist_page'))

        return '<h1 text-center>Invalid username or password</h1>'
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    return redirect(url_for('home_page'))


@app.route('/delete/<int:task_id>')
def delete(task_id):

    delete_task = Task.query.filter_by(task_id=task_id).first()
    db.session.delete(delete_task)
    db.session.commit()
    return redirect(url_for('mylist_page'))


@app.route('/update/<int:task_id>', methods=['GET', 'POST'])
def update_page(task_id):
    form = EditItemForm()
    if form.validate_on_submit():
        update_task = Task.query.filter_by(task_id=task_id).first()
        update_task.task_title = form.edit_item.data
        update_task.task_desc = form.edit_desc.data
        # Task(task_title=form.edit_item.data ,
        #                 task_desc=form.edit_desc.data,
        #                 )
        db.session.add(update_task)
        db.session.commit()
        return redirect(url_for('mylist_page'))

    updated = Task.query.filter_by(task_id=task_id).first()
    #items = Task.query.all()
    return render_template("update.html", form=form, updated=updated)


if __name__ == "__main__":
    app.run(debug=True)


# <p>You can use the mark tag to <mark>highlight</mark> text.</p>
# <p><del>This line of text is meant to be treated as deleted text.</del></p>
