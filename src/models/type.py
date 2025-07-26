from src.models.user import db
import uuid

class Type(db.Model):
    __tablename__ = 'types'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Relationship
    category = db.relationship('Category', backref='types')
    
    # Unique constraint: name should be unique within a category
    __table_args__ = (db.UniqueConstraint('name', 'category_id', name='unique_type_per_category'),)
    
    def __init__(self, name, category_id, description=None):
        self.name = name
        self.category_id = category_id
        self.description = description
    
    def to_dict(self):
        """Convert the type object to a dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'description': self.description,
            'content_count': len(self.content_items) if hasattr(self, 'content_items') else 0
        }
    
    def __repr__(self):
        return f'<Type {self.name} in {self.category.name if self.category else "Unknown"}>'

