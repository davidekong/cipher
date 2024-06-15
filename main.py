from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, Blueprint, render_template
from events import socketio
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from datetime import datetime
from werkzeug.utils import secure_filename
import json
from flask import Flask, render_template, request, redirect, url_for, send_file, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from io import BytesIO
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask import render_template, url_for, flash, redirect
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sigmoid'




socketio.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


friends = db.Table('friends',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user):
    return User.query.get(int(user))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    friends = db.relationship(
        'User',
        secondary=friends,
        primaryjoin=id==friends.c.user_id,
        secondaryjoin=id==friends.c.friend_id,
        backref='friend_of'
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def add_friend(self, user):
        if user not in self.friends:
            self.friends.append(user)
        if self not in user.friends:
            user.friends.append(self)

    def remove_friend(self, user):
        if user in self.friends:
            self.friends.remove(user)
        if self in user.friends:
            user.friends.remove(self)

    def is_friend(self, user):
        return user in self.friends

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
    
class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sent_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    package_type = db.Column(db.String(50), nullable=False)
    content_id = db.Column(db.Integer, nullable=False)
    has_access = db.Column(db.Boolean, default=False, nullable=False)

    owner = db.relationship('User', foreign_keys=[owner_id])
    sender = db.relationship('User', foreign_keys=[sender_id])
    recipient = db.relationship('User', foreign_keys=[recipient_id])

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_content = db.Column(db.LargeBinary, nullable=False)
    description = db.Column(db.String(500))



    
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
    

with app.app_context():
    db.drop_all()
    db.create_all()

    for i in range(1, 11):  # u1 to u10
        user = User(
            username=f"u{i}",
            email=f"u{i}@mail.com"
        )
        user.set_password("test")
        db.session.add(user)

    db.session.commit()

    print("✅ Users created successfully!")
    users = User.query.all()
    for user in users:
        print(user)
        
    u1 = User.query.filter_by(username='u1').first()
    u2 = User.query.filter_by(username='u2').first()
    u3 = User.query.filter_by(username='u3').first()
    u4 = User.query.filter_by(username='u4').first()
    u5 = User.query.filter_by(username='u5').first()

    # Make friends
    u1.add_friend(u2)
    u1.add_friend(u3)

    u2.add_friend(u4)

    u3.add_friend(u4)
    u3.add_friend(u5)

    db.session.commit()

    # Display friendships
    def show_friends(user):
        print(f"{user.username}'s friends: {[f.username for f in user.friends]}")

    show_friends(u1)
    show_friends(u2)
    show_friends(u3)
    show_friends(u4)
    show_friends(u5)
    
    
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    id = session.get('id', None)
    user = User.query.get(id)
    return render_template('home.html')






@app.route('/send_picture', methods=['GET', 'POST'])
@login_required
def send_picture():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            recipient_username = request.form['recipient_username']
            recipient = User.query.filter_by(username=recipient_username).first()
            if not recipient:
                flash('Recipient not found.', 'error')
                return redirect(url_for('send_picture'))

            filename = secure_filename(file.filename)
            image = Image(filename=filename, data=file.read())
            db.session.add(image)
            db.session.commit()

            package = Package(
                owner_id=current_user.id,
                sender_id=current_user.id,
                recipient_id=recipient.id,
                package_type='image',
                content_id=image.id,
                sent_at=datetime.utcnow(),
                has_access=True
            )

            db.session.add(package)
            db.session.commit()
            return redirect(url_for('send_picture'))

    # Fetch packages and current user's friends
    packages = Package.query.filter_by(recipient_id=current_user.id, has_access=True, package_type='image').all()
    images = [(pkg.sent_at, pkg.sender.username, Image.query.get(pkg.content_id)) for pkg in packages]
    friends = current_user.friends  # 💥 Get the friends

    return render_template('send_picture.html', images=images, friends=friends)



@app.route('/image/<int:image_id>')
@login_required
def get_image(image_id):
    image = Image.query.get(image_id)
    return send_file(BytesIO(image.data), mimetype='image/jpeg')


@app.route('/show_image/<int:image_id>')
@login_required
def show_image(image_id):
    image = Image.query.get(image_id)
    data = {
        'image': image,
        'current_user': current_user
    }
    
    return render_template('show_image.html', data=data)


@app.route('/outbox', methods=['GET', 'POST'])
@login_required
def outbox():
    user = current_user
    packages = Package.query.filter_by(owner_id=user.id, package_type="image").all()
    image_details = []
    content_ids_checked = []
    for package in packages:
        image = Image.query.get(package.content_id)
        if package.content_id in content_ids_checked:
            continue
        content_ids_checked.append(package.content_id)
        image_details.append({
            'package_id': package.id,
            'filename': image.filename,
            'sent_at': package.sent_at,
            'sender': package.sender.username,
            'recipient': package.recipient.username,
            'content_id': package.content_id,
            'current_user': current_user,
        })
    return render_template('outbox.html', image_details=image_details)

@app.route('/share_image/<int:image_id>', methods=['GET', 'POST'])
@login_required
def share_image(image_id):
    image = Image.query.get(image_id)
    if request.method == 'POST':
        recipient_username = request.form['recipient_username']
            
        recipient = User.query.filter_by(username=recipient_username).first()
        
        if not recipient:
            flash('Recipient not found.', 'error')
            return redirect(url_for('send_picture'))
        
        initial_package = Package.query.filter_by(content_id=image_id, package_type='image').first()
        owner_id = initial_package.owner_id
        package = Package(
            owner_id=owner_id,
            sender_id=current_user.id,
            recipient_id=recipient.id,
            package_type='image',
            content_id=image.id,
            sent_at=datetime.utcnow(),
            has_access=False
        )
        
        db.session.add(package)
        db.session.commit()
        return redirect(url_for('send_picture'))
    return render_template('share_image.html', image=image)

@app.route('/my_image_packages')
@login_required
def my_image_packages():
    user_id = current_user.id  # Assuming `g.user` is set to the current user
    image_packages = Package.query.filter_by(recipient_id=user_id, package_type='image').all()
    image_details = []
    content_ids_checked = []
    for package in image_packages:
        image = Image.query.get(package.content_id)
        if package.content_id in content_ids_checked:
            continue
        content_ids_checked.append(package.content_id)
        image_details.append({
            'package_id': package.id,
            'filename': image.filename,
            'sent_at': package.sent_at,
            'sender': package.sender.username,
            'recipient': package.recipient.username,
            'content_id': package.content_id,
            'current_user': current_user
        })
    return render_template('my_image_packages.html', image_details=image_details)

@app.route('/grant_access', methods=['GET', 'POST'])
@login_required
def grant_access():
    if request.method == 'POST':
        package_id = request.form.get('package_id')
        package = Package.query.get(package_id)
        if package:
            package.has_access = True
            db.session.commit()
            return redirect(url_for('grant_access'))
    packages = Package.query.filter_by(owner_id=current_user.id, has_access=False, package_type='image').all()
    
    return render_template('grant_access.html', packages=packages)

def get_package_hierarchy(package_id, root_user_id):
    
    root_user = User.query.get(root_user_id)
    hierarchy = {'name': root_user.username, 'children': []}
    root_package = Package.query.filter_by(id=package_id).first()
    image_id = root_package.content_id
    def build_hierarchy(user_id):
        children = []
        packages = Package.query.filter_by(content_id=image_id, sender_id=user_id).all()
        for package in packages:
            recipient = User.query.get(package.recipient_id)
            child_hierarchy = {'name': recipient.username, 'children': build_hierarchy(recipient.id)}
            children.append(child_hierarchy)
        return children
    
    hierarchy['children'] = build_hierarchy(root_user_id)
    return hierarchy

@app.route('/package_hierarchy/<int:package_id>/<int:root_user_id>', methods=['GET'])
@login_required
def package_hierarchy(package_id, root_user_id):
    hierarchy = get_package_hierarchy(package_id, root_user_id)
    return jsonify(hierarchy)


@app.route('/tree/<int:package_id>')
@login_required
def tree(package_id):
    data = {
        "package_id": package_id,
        "current_user_id": current_user.id
    }
    return render_template('tree.html', data=data)

@app.route('/vid')
def vid():
    return render_template('vid.html')


if __name__ == "__main__":
    socketio.run(app, debug=True)



    
    
