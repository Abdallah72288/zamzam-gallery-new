from src.models.user import db
import uuid

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    icon_url = db.Column(db.String(500), nullable=True)
    
    def __init__(self, name, description=None, icon_url=None):
        self.name = name
        self.description = description
        self.icon_url = icon_url
    
    def to_dict(self):
        """Convert the category object to a dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon_url': self.icon_url,
            'content_count': len(self.content_items) if hasattr(self, 'content_items') else 0
        }
    
    def __repr__(self):
        return f'<Category {self.name}>'

