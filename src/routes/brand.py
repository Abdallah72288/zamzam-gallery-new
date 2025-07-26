from flask import Blueprint, request, jsonify
from src.models.brand import Brand, db

brand_bp = Blueprint('brand', __name__)

@brand_bp.route('/brands', methods=['GET'])
def get_all_brands():
    """Get all brands"""
    try:
        brands = Brand.query.all()
        return jsonify({
            'success': True,
            'brands': [brand.to_dict() for brand in brands]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@brand_bp.route('/brands/<brand_id>', methods=['GET'])
def get_brand(brand_id):
    """Get a specific brand"""
    try:
        brand = Brand.query.get_or_404(brand_id)
        return jsonify({
            'success': True,
            'brand': brand.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@brand_bp.route('/brands', methods=['POST'])
def create_brand():
    """Create a new brand"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'success': False, 'error': 'اسم العلامة التجارية مطلوب'}), 400
        
        # Check if brand already exists
        existing_brand = Brand.query.filter_by(name=data['name']).first()
        if existing_brand:
            return jsonify({'success': False, 'error': 'العلامة التجارية موجودة بالفعل'}), 400
        
        brand = Brand(
            name=data['name'],
            logo_url=data.get('logo_url'),
            website_url=data.get('website_url'),
            description=data.get('description')
        )
        
        db.session.add(brand)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء العلامة التجارية بنجاح',
            'brand': brand.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@brand_bp.route('/brands/<brand_id>', methods=['PUT'])
def update_brand(brand_id):
    """Update a brand"""
    try:
        brand = Brand.query.get_or_404(brand_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'لا توجد بيانات للتحديث'}), 400
        
        # Check if new name already exists (if name is being changed)
        if 'name' in data and data['name'] != brand.name:
            existing_brand = Brand.query.filter_by(name=data['name']).first()
            if existing_brand:
                return jsonify({'success': False, 'error': 'اسم العلامة التجارية موجود بالفعل'}), 400
        
        # Update fields
        if 'name' in data:
            brand.name = data['name']
        if 'logo_url' in data:
            brand.logo_url = data['logo_url']
        if 'website_url' in data:
            brand.website_url = data['website_url']
        if 'description' in data:
            brand.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث العلامة التجارية بنجاح',
            'brand': brand.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@brand_bp.route('/brands/<brand_id>', methods=['DELETE'])
def delete_brand(brand_id):
    """Delete a brand"""
    try:
        brand = Brand.query.get_or_404(brand_id)
        
        # Check if brand has content
        if hasattr(brand, 'content_items') and len(brand.content_items) > 0:
            return jsonify({
                'success': False, 
                'error': 'لا يمكن حذف العلامة التجارية لأنها تحتوي على محتوى'
            }), 400
        
        db.session.delete(brand)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم حذف العلامة التجارية بنجاح'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

