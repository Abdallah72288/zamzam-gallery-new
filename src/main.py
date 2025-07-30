import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, send_file
from flask_cors import CORS
from datetime import datetime

# Import database instance
from src.models.user import db

# Import all models to ensure they are registered
from src.models.user import User
from src.models.content import Content
from src.models.category import Category
from src.models.type import Type
from src.models.brand import Brand
from src.models.settings import Settings

# Import all routes
from src.routes.user import user_bp
from src.routes.content import content_bp
from src.routes.category import category_bp
from src.routes.type import type_bp
from src.routes.brand import brand_bp
from src.routes.settings import settings_bp

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
app.register_blueprint(settings_bp, url_prefix='/api')

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
    
    # Create default settings
    default_settings = [
        # Theme settings
        {'key': 'theme_mode', 'value': 'light', 'description': 'وضع السمة (فاتح/داكن)'},
        {'key': 'primary_color', 'value': '#6366f1', 'description': 'اللون الأساسي للموقع'},
        {'key': 'font_family', 'value': 'Cairo', 'description': 'خط الموقع'},
        {'key': 'background_style', 'value': 'gradient', 'description': 'نمط الخلفية'},
        
        # Social media settings
        {'key': 'social_facebook', 'value': '', 'description': 'رابط حساب Facebook'},
        {'key': 'social_twitter', 'value': '', 'description': 'رابط حساب Twitter'},
        {'key': 'social_instagram', 'value': '', 'description': 'رابط حساب Instagram'},
        {'key': 'social_linkedin', 'value': '', 'description': 'رابط حساب LinkedIn'},
        {'key': 'social_youtube', 'value': '', 'description': 'رابط حساب YouTube'},
        {'key': 'social_github', 'value': 'https://github.com/Abdallah72288', 'description': 'رابط حساب GitHub'},
        {'key': 'social_telegram', 'value': '', 'description': 'رابط حساب Telegram'},
        {'key': 'social_whatsapp', 'value': '', 'description': 'رابط حساب WhatsApp'},
        
        # SEO settings
        {'key': 'seo_site_title', 'value': 'معرض زمزم - Abdallah', 'description': 'عنوان الموقع'},
        {'key': 'seo_site_description', 'value': 'منصة متطورة لعرض وإدارة الصور والفيديوهات مع إمكانيات رفع متقدمة من الهاتف وإدارة شاملة للتصنيفات والعلامات التجارية', 'description': 'وصف الموقع'},
        {'key': 'seo_site_keywords', 'value': 'معرض صور, فيديوهات, رفع ملفات, تصوير, Abdallah, زمزم, gallery, photos, videos', 'description': 'كلمات مفتاحية للموقع'},
        {'key': 'seo_site_author', 'value': 'Abdallah', 'description': 'مؤلف الموقع'},
        {'key': 'seo_site_url', 'value': 'https://p9hwiqclzlpy.manus.space', 'description': 'رابط الموقع'},
        
        # Developer mode
        {'key': 'developer_mode_enabled', 'value': 'false', 'description': 'تفعيل وضع المطور'}
    ]
    
    for setting_data in default_settings:
        if not Settings.query.filter_by(key=setting_data['key']).first():
            setting = Settings(
                key=setting_data['key'],
                value=setting_data['value'],
                description=setting_data['description']
            )
            db.session.add(setting)
    
    # Commit all changes
    db.session.commit()

# Main routes
@app.route('/')
def index():
    """Main page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/favicon.ico')
def favicon():
    """Favicon"""
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/manifest.json')
def manifest():
    """PWA Manifest"""
    return send_from_directory(app.static_folder, 'manifest.json', mimetype='application/json')

@app.route('/sitemap.xml')
def sitemap():
    """XML Sitemap for SEO"""
    return send_from_directory(app.static_folder, 'sitemap.xml', mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    """Robots.txt for SEO"""
    return send_from_directory(app.static_folder, 'robots.txt', mimetype='text/plain')

@app.route('/sw.js')
def service_worker():
    """Service Worker for PWA"""
    return send_from_directory(app.static_folder, 'sw.js', mimetype='application/javascript')

# SEO-friendly routes
@app.route('/gallery')
@app.route('/gallery/')
def gallery_page():
    """Gallery page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/upload')
@app.route('/upload/')
def upload_page():
    """Upload page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/management')
@app.route('/management/')
def management_page():
    """Management page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/categories')
@app.route('/categories/')
def categories_page():
    """Categories page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/types')
@app.route('/types/')
def types_page():
    """Types page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/brands')
@app.route('/brands/')
def brands_page():
    """Brands page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/search')
@app.route('/search/')
def search_page():
    """Search page"""
    return send_from_directory(app.static_folder, 'index.html')

# API route for generating dynamic sitemap
@app.route('/api/sitemap')
def api_sitemap():
    """Generate dynamic sitemap with content URLs"""
    try:
        # Get all content
        content_items = Content.query.order_by(Content.created_at.desc()).all()
        
        # Get all categories
        categories = Category.query.order_by(Category.created_at.desc()).all()
        
        # Get all types
        types = Type.query.order_by(Type.created_at.desc()).all()
        
        # Get all brands
        brands = Brand.query.order_by(Brand.created_at.desc()).all()
        
        sitemap_data = {
            'content': [{'id': item.id, 'title': item.title, 'created_at': item.created_at.isoformat()} for item in content_items],
            'categories': [{'id': cat.id, 'name': cat.name, 'created_at': cat.created_at.isoformat()} for cat in categories],
            'types': [{'id': type_item.id, 'name': type_item.name, 'created_at': type_item.created_at.isoformat()} for type_item in types],
            'brands': [{'id': brand.id, 'name': brand.name, 'created_at': brand.created_at.isoformat()} for brand in brands]
        }
        
        return jsonify(sitemap_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=True)

