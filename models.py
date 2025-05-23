from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Association table for the many-to-many relationship between users (friends)
friends = db.Table('friends',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    """
    User model for storing user information and managing friendships.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    # Relationship for friends (self-referential many-to-many)
    friends = db.relationship(
        'User',
        secondary=friends,
        primaryjoin=id==friends.c.user_id,
        secondaryjoin=id==friends.c.friend_id,
        backref='friend_of'
    )

    # Set the user's password (hashed)
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    # Check the user's password
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    # Add a friend (bidirectional)
    def add_friend(self, user):
        if user not in self.friends:
            self.friends.append(user)
        if self not in user.friends:
            user.friends.append(self)

    # Remove a friend (bidirectional)
    def remove_friend(self, user):
        if user in self.friends:
            self.friends.remove(user)
        if self in user.friends:
            user.friends.remove(self)

    # Check if another user is a friend
    def is_friend(self, user):
        return user in self.friends

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

# Package model for tracking sent/received images and videos
class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sent_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    package_type = db.Column(db.String(50), nullable=False)
    content_id = db.Column(db.Integer, nullable=False)
    has_access = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships for owner, sender, and recipient
    owner = db.relationship('User', foreign_keys=[owner_id])
    sender = db.relationship('User', foreign_keys=[sender_id])
    recipient = db.relationship('User', foreign_keys=[recipient_id])

# Message model for storing text messages
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

# Image model for storing image files
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

# Video model for storing video files
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_content = db.Column(db.LargeBinary, nullable=False)
    description = db.Column(db.String(500))