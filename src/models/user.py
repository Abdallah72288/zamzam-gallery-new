from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import hashlib

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum('admin', 'uploader', 'viewer', name='user_role_enum'), default='uploader')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, username, email, password, role='uploader'):
        self.username = username
        self.email = email
        self.password_hash = self.hash_password(password)
        self.role = role
    
    def hash_password(self, password):
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        return self.password_hash == self.hash_password(password)
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_sensitive=False):
        """Convert the user object to a dictionary for JSON serialization"""
        user_dict = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            user_dict['password_hash'] = self.password_hash
        
        return user_dict
    
    def __repr__(self):
        return f'<User {self.username}>'

