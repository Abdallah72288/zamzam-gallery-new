from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.settings import Settings

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET'])
def get_all_settings():
    """Get all settings"""
    try:
        settings = Settings.query.all()
        return jsonify({
            'success': True,
            'settings': [setting.to_dict() for setting in settings]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/settings/<key>', methods=['GET'])
def get_setting(key):
    """Get a specific setting by key"""
    try:
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            return jsonify({
                'success': True,
                'setting': setting.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'الإعداد غير موجود'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/settings/<key>', methods=['POST', 'PUT'])
def set_setting(key):
    """Set a setting value"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'لا توجد بيانات'}), 400
        
        value = data.get('value')
        description = data.get('description')
        
        setting = Settings.set_setting(key, value, description)
        
        return jsonify({
            'success': True,
            'message': 'تم حفظ الإعداد بنجاح',
            'setting': setting.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/settings/<key>', methods=['DELETE'])
def delete_setting(key):
    """Delete a setting"""
    try:
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            db.session.delete(setting)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'تم حذف الإعداد بنجاح'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'الإعداد غير موجود'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/settings/theme', methods=['GET'])
def get_theme_settings():
    """Get theme settings"""
    try:
        theme_settings = Settings.get_theme_settings()
        return jsonify({
            'success': True,
            'theme': theme_settings
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/settings/theme', methods=['POST'])
def update_theme_settings():
    """Update theme settings"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'لا توجد بيانات'}), 400
        
        # Update theme settings
        if 'theme_mode' in data:
            Settings.set_setting('theme_mode', data['theme_mode'], 'وضع السمة (فاتح/داكن)')
        
        if 'primary_color' in data:
            Settings.set_setting('primary_color', data['primary_color'], 'اللون الأساسي للموقع')
        
        if 'font_family' in data:
            Settings.set_setting('font_family', data['font_family'], 'خط الموقع')
        
        if 'background_style' in data:
            Settings.set_setting('background_style', data['background_style'], 'نمط الخلفية')
        
        # Get updated settings
        updated_settings = Settings.get_theme_settings()
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث إعدادات السمة بنجاح',
            'theme': updated_settings
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/settings/social-media', methods=['GET'])
def get_social_media_settings():
    """Get social media links"""
    try:
        social_links = Settings.get_social_media_links()
        return jsonify({
            'success': True,
            'social_media': social_links
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/settings/social-media', methods=['POST'])
def update_social_media_settings():
    """Update social media links"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'لا توجد بيانات'}), 400
        
        # Update social media links
        Settings.set_social_media_links(data)
        
        # Get updated links
        updated_links = Settings.get_social_media_links()
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث روابط التواصل الاجتماعي بنجاح',
            'social_media': updated_links
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/settings/seo', methods=['GET'])
def get_seo_settings():
    """Get SEO settings"""
    try:
        seo_settings = Settings.get_seo_settings()
        return jsonify({
            'success': True,
            'seo': seo_settings
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/settings/seo', methods=['POST'])
def update_seo_settings():
    """Update SEO settings"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'لا توجد بيانات'}), 400
        
        # Update SEO settings
        if 'site_title' in data:
            Settings.set_setting('seo_site_title', data['site_title'], 'عنوان الموقع')
        
        if 'site_description' in data:
            Settings.set_setting('seo_site_description', data['site_description'], 'وصف الموقع')
        
        if 'site_keywords' in data:
            Settings.set_setting('seo_site_keywords', data['site_keywords'], 'كلمات مفتاحية للموقع')
        
        if 'site_author' in data:
            Settings.set_setting('seo_site_author', data['site_author'], 'مؤلف الموقع')
        
        if 'site_url' in data:
            Settings.set_setting('seo_site_url', data['site_url'], 'رابط الموقع')
        
        # Get updated settings
        updated_settings = Settings.get_seo_settings()
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث إعدادات SEO بنجاح',
            'seo': updated_settings
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/settings/developer-mode', methods=['GET'])
def get_developer_mode_status():
    """Get developer mode status"""
    try:
        is_enabled = Settings.get_setting('developer_mode_enabled', False)
        return jsonify({
            'success': True,
            'developer_mode_enabled': is_enabled
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@settings_bp.route('/settings/developer-mode', methods=['POST'])
def toggle_developer_mode():
    """Toggle developer mode"""
    try:
        data = request.get_json()
        enabled = data.get('enabled', False) if data else False
        
        Settings.set_setting('developer_mode_enabled', enabled, 'تفعيل وضع المطور')
        
        return jsonify({
            'success': True,
            'message': f'تم {"تفعيل" if enabled else "إلغاء"} وضع المطور',
            'developer_mode_enabled': enabled
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

