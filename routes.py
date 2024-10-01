from flask import Blueprint, render_template, redirect, url_for, flash, request, session, send_file, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from models import User, Package, Image, Video, db
from forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from io import BytesIO
from datetime import datetime
from utils import get_package_hierarchy

main_blueprint = Blueprint('main', __name__)

def show_friends(user):
    print(f"{user.username}'s friends: {[f.username for f in user.friends]}")

@main_blueprint.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main_blueprint.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main_blueprint.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main_blueprint.route('/')
@login_required
def home():
    return render_template('home.html')

@main_blueprint.route('/send_picture', methods=['GET', 'POST'])
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
                return redirect(request.url)  # Redirect if recipient not found

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

    # Fetch packages and current user's friends
    packages = Package.query.filter_by(recipient_id=current_user.id, has_access=True, package_type='image').all()
    images = [(pkg.sent_at, pkg.sender.username, Image.query.get(pkg.content_id)) for pkg in packages]
    friends = current_user.friends  # 💥 Get the friends

    return render_template('send_picture.html', images=images, friends=friends)

@main_blueprint.route('/image/<int:image_id>')
@login_required
def get_image(image_id):
    image = Image.query.get(image_id)
    return send_file(BytesIO(image.data), mimetype='image/jpeg')

@main_blueprint.route('/show_image/<int:image_id>')
@login_required
def show_image(image_id):
    image = Image.query.get(image_id)
    data = {
        'image': image,
        'current_user': current_user
    }
    return render_template('show_image.html', **data)

@main_blueprint.route('/outbox', methods=['GET', 'POST'])
@login_required
def outbox():
    return render_template('outbox.html')

@main_blueprint.route('/share_image/<int:image_id>', methods=['GET', 'POST'])
@login_required
def share_image(image_id):
     return render_template('share_image.html')
 
 
@main_blueprint.route('/my_image_packages')
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


@main_blueprint.route('/grant_access', methods=['GET', 'POST'])
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


@main_blueprint.route('/package_hierarchy/<int:package_id>/<int:root_user_id>', methods=['GET'])
@login_required
def package_hierarchy(package_id, root_user_id):
    hierarchy = get_package_hierarchy(package_id, root_user_id)
    return jsonify(hierarchy)


@main_blueprint.route('/tree/<int:package_id>')
@login_required
def tree(package_id):
    data = {
        "package_id": package_id,
        "current_user_id": current_user.id
    }
    return render_template('tree.html', data=data)