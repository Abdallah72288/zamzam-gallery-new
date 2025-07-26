from src.models.user import db
from datetime import datetime
import uuid
import json

class Content(db.Model):
    __tablename__ = 'content'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_url = db.Column(db.String(500), nullable=False)
    thumbnail_url = db.Column(db.String(500), nullable=True)
    content_type = db.Column(db.Enum('image', 'video', name='content_type_enum'), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    views_count = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)
    
    # Foreign Keys
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=False)
    type_id = db.Column(db.String(36), db.ForeignKey('types.id'), nullable=True)
    brand_id = db.Column(db.String(36), db.ForeignKey('brands.id'), nullable=True)
    uploaded_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Additional fields
    tags = db.Column(db.Text, nullable=True)  # JSON string of tags array
    is_public = db.Column(db.Boolean, default=True)
    content_metadata = db.Column(db.Text, nullable=True)  # JSON string for additional metadata
    
    # Relationships
    category = db.relationship('Category', backref='content_items')
    type = db.relationship('Type', backref='content_items')
    brand = db.relationship('Brand', backref='content_items')
    uploader = db.relationship('User', backref='uploaded_content')
    
    def __init__(self, title, file_url, content_type, category_id, uploaded_by, **kwargs):
        self.title = title
        self.file_url = file_url
        self.content_type = content_type
        self.category_id = category_id
        self.uploaded_by = uploaded_by
        
        # Optional fields
        self.description = kwargs.get('description')
        self.thumbnail_url = kwargs.get('thumbnail_url')
        self.type_id = kwargs.get('type_id')
        self.brand_id = kwargs.get('brand_id')
        self.is_public = kwargs.get('is_public', True)
        
        # Handle tags as JSON
        if 'tags' in kwargs and kwargs['tags']:
            if isinstance(kwargs['tags'], list):
                self.tags = json.dumps(kwargs['tags'])
            else:
                self.tags = kwargs['tags']
        
        # Handle metadata as JSON
        if 'metadata' in kwargs and kwargs['metadata']:
            if isinstance(kwargs['metadata'], dict):
                self.content_metadata = json.dumps(kwargs['metadata'])
            else:
                self.content_metadata = kwargs['metadata']
    
    def get_tags(self):
        """Return tags as a list"""
        if self.tags:
            try:
                return json.loads(self.tags)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_tags(self, tags_list):
        """Set tags from a list"""
        if isinstance(tags_list, list):
            self.tags = json.dumps(tags_list)
        else:
            self.tags = None
    
    def get_metadata(self):
        """Return metadata as a dictionary"""
        if self.content_metadata:
            try:
                return json.loads(self.content_metadata)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_metadata(self, metadata_dict):
        """Set metadata from a dictionary"""
        if isinstance(metadata_dict, dict):
            self.content_metadata = json.dumps(metadata_dict)
        else:
            self.content_metadata = None
    
    def increment_views(self):
        """Increment the views count"""
        self.views_count += 1
        db.session.commit()
    
    def increment_likes(self):
        """Increment the likes count"""
        self.likes_count += 1
        db.session.commit()
    
    def to_dict(self):
        """Convert the content object to a dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'file_url': self.file_url,
            'thumbnail_url': self.thumbnail_url,
            'content_type': self.content_type,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'views_count': self.views_count,
            'likes_count': self.likes_count,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'type_id': self.type_id,
            'type_name': self.type.name if self.type else None,
            'brand_id': self.brand_id,
            'brand_name': self.brand.name if self.brand else None,
            'uploaded_by': self.uploaded_by,
            'uploader_name': self.uploader.username if self.uploader else None,
            'tags': self.get_tags(),
            'is_public': self.is_public,
            'metadata': self.get_metadata()
        }
    
    def __repr__(self):
        return f'<Content {self.title}>'

