from src.models.user import db
import uuid
import json

class Settings(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def __init__(self, key, value=None, description=None):
        self.key = key
        if isinstance(value, (dict, list)):
            self.value = json.dumps(value, ensure_ascii=False)
        else:
            self.value = value
        self.description = description
    
    def get_value(self):
        """Return value as appropriate type"""
        if self.value is None:
            return None
        
        # Try to parse as JSON first
        try:
            return json.loads(self.value)
        except (json.JSONDecodeError, TypeError):
            # If not JSON, return as string
            return self.value
    
    def set_value(self, value):
        """Set value with automatic JSON encoding for complex types"""
        if isinstance(value, (dict, list)):
            self.value = json.dumps(value, ensure_ascii=False)
        else:
            self.value = str(value) if value is not None else None
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.get_value(),
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_setting(key, default=None):
        """Get a setting value by key"""
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            return setting.get_value()
        return default
    
    @staticmethod
    def set_setting(key, value, description=None):
        """Set a setting value by key"""
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            setting.set_value(value)
            if description:
                setting.description = description
        else:
            setting = Settings(key=key, value=value, description=description)
            db.session.add(setting)
        
        db.session.commit()
        return setting
    
    @staticmethod
    def get_theme_settings():
        """Get all theme-related settings"""
        return {
            'theme_mode': Settings.get_setting('theme_mode', 'light'),
            'primary_color': Settings.get_setting('primary_color', '#6366f1'),
            'font_family': Settings.get_setting('font_family', 'Cairo'),
            'background_style': Settings.get_setting('background_style', 'gradient')
        }
    
    @staticmethod
    def get_social_media_links():
        """Get all social media links"""
        return {
            'facebook': Settings.get_setting('social_facebook', ''),
            'twitter': Settings.get_setting('social_twitter', ''),
            'instagram': Settings.get_setting('social_instagram', ''),
            'linkedin': Settings.get_setting('social_linkedin', ''),
            'youtube': Settings.get_setting('social_youtube', ''),
            'github': Settings.get_setting('social_github', ''),
            'telegram': Settings.get_setting('social_telegram', ''),
            'whatsapp': Settings.get_setting('social_whatsapp', '')
        }
    
    @staticmethod
    def set_social_media_links(links):
        """Set all social media links"""
        for platform, url in links.items():
            Settings.set_setting(f'social_{platform}', url, f'رابط حساب {platform}')
    
    @staticmethod
    def get_seo_settings():
        """Get SEO-related settings"""
        return {
            'site_title': Settings.get_setting('seo_site_title', 'معرض زمزم - Abdallah'),
            'site_description': Settings.get_setting('seo_site_description', 'منصة متطورة لعرض وإدارة الصور والفيديوهات مع إمكانيات رفع متقدمة من الهاتف'),
            'site_keywords': Settings.get_setting('seo_site_keywords', 'معرض صور, فيديوهات, رفع ملفات, تصوير, Abdallah'),
            'site_author': Settings.get_setting('seo_site_author', 'Abdallah'),
            'site_url': Settings.get_setting('seo_site_url', 'https://p9hwiqclzlpy.manus.space')
        }
    
    def __repr__(self):
        return f'<Settings {self.key}: {self.value}>'

