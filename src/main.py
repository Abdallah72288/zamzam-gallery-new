import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS

# Import database instance
from src.models.user import db

# Import all models to ensure they are registered
from src.models.user import User
from src.models.content import Content
from src.models.category import Category
from src.models.type import Type
from src.models.brand import Brand

# Import all routes
from src.routes.user import user_bp
from src.routes.content import content_bp
from src.routes.category import category_bp
from src.routes.type import type_bp
from src.routes.brand import brand_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'zamzam-gallery-secret-key-2025'

# Enable CORS for all routes
CORS(app, origins="*")

# Configure file upload
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')

# Register all blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(content_bp, url_prefix='/api')
app.register_blueprint(category_bp, url_prefix='/api')
app.register_blueprint(type_bp, url_prefix='/api')
app.register_blueprint(brand_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create all tables and add sample data
with app.app_context():
    db.create_all()
    
    # Create default user if not exists
    if not User.query.filter_by(username='abdallah').first():
        default_user = User(
            username='abdallah',
            email='abdallah@zamzam-gallery.com',
            password='admin123',
            role='admin'
        )
        db.session.add(default_user)
    
    # Create default categories if not exist
    default_categories = [
        {'name': 'طبيعة', 'description': 'صور ومقاطع فيديو للطبيعة والمناظر الطبيعية'},
        {'name': 'فن', 'description': 'أعمال فنية ولوحات وتصاميم إبداعية'},
        {'name': 'تقنية', 'description': 'صور ومقاطع فيديو متعلقة بالتكنولوجيا'},
        {'name': 'رياضة', 'description': 'صور ومقاطع فيديو رياضية'},
        {'name': 'طعام', 'description': 'صور الطعام والمأكولات'},
        {'name': 'سفر', 'description': 'صور ومقاطع فيديو من الرحلات والسفر'},
        {'name': 'أشخاص', 'description': 'صور الأشخاص والبورتريه'},
        {'name': 'معمارية', 'description': 'صور المباني والهندسة المعمارية'}
    ]
    
    for cat_data in default_categories:
        if not Category.query.filter_by(name=cat_data['name']).first():
            category = Category(name=cat_data['name'], description=cat_data['description'])
            db.session.add(category)
    
    # Create default types for nature category
    nature_category = Category.query.filter_by(name='طبيعة').first()
    if nature_category:
        default_types = [
            {'name': 'جبال', 'description': 'صور ومقاطع فيديو للجبال'},
            {'name': 'بحر', 'description': 'صور ومقاطع فيديو للبحر والمحيطات'},
            {'name': 'صحراء', 'description': 'صور ومقاطع فيديو للصحراء'},
            {'name': 'غابات', 'description': 'صور ومقاطع فيديو للغابات'},
            {'name': 'حيوانات', 'description': 'صور ومقاطع فيديو للحيوانات'}
        ]
        
        for type_data in default_types:
            if not Type.query.filter_by(name=type_data['name'], category_id=nature_category.id).first():
                type_obj = Type(
                    name=type_data['name'], 
                    category_id=nature_category.id, 
                    description=type_data['description']
                )
                db.session.add(type_obj)
    
    # Create default brands
    default_brands = [
        {'name': 'Canon', 'description': 'كاميرات ومعدات تصوير'},
        {'name': 'Nikon', 'description': 'كاميرات ومعدات تصوير'},
        {'name': 'Sony', 'description': 'كاميرات ومعدات إلكترونية'},
        {'name': 'Apple', 'description': 'أجهزة iPhone وiPad'},
        {'name': 'Samsung', 'description': 'هواتف ذكية وأجهزة إلكترونية'}
    ]
    
    for brand_data in default_brands:
        if not Brand.query.filter_by(name=brand_data['name']).first():
            brand = Brand(name=brand_data['name'], description=brand_data['description'])
            db.session.add(brand)
    
    # Commit all changes
    db.session.commit()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.errorhandler(413)
def too_large(e):
    return {"success": False, "error": "الملف كبير جداً. الحد الأقصى 100 ميجابايت"}, 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

