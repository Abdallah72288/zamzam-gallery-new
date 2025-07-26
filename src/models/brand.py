from src.models.user import db
import uuid

class Brand(db.Model):
    __tablename__ = 'brands'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False, unique=True)
    logo_url = db.Column(db.String(500), nullable=True)
    website_url = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    def __init__(self, name, logo_url=None, website_url=None, description=None):
        self.name = name
        self.logo_url = logo_url
        self.website_url = website_url
        self.description = description
    
    def to_dict(self):
        """Convert the brand object to a dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'logo_url': self.logo_url,
            'website_url': self.website_url,
            'description': self.description,
            'content_count': len(self.content_items) if hasattr(self, 'content_items') else 0
        }
    
    def __repr__(self):
        return f'<Brand {self.name}>'

