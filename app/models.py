from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


class CockatilDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    ingredients = db.Column(db.Text(), nullable=False)
    preparation = db.Column(db.Text(), nullable=False)


    
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
    messages_sent = db.relationship('UserMessage',
                                    foreign_keys='UserMessage.sender_id',
                                    backref='author', lazy='dynamic')
    message_recived = db.relationship('UserMessage',
                                      foreign_keys='UserMessage.recipient_id',
                                      backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
   
class UserMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    subject = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Message {}>'.format(self.body)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))