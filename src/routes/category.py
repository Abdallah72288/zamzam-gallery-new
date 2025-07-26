from flask import Blueprint, request, jsonify
from src.models.category import Category, db

category_bp = Blueprint('category', __name__)

@category_bp.route('/categories', methods=['GET'])
def get_all_categories():
    """Get all categories"""
    try:
        categories = Category.query.all()
        return jsonify({
            'success': True,
            'categories': [category.to_dict() for category in categories]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@category_bp.route('/categories/<category_id>', methods=['GET'])
def get_category(category_id):
    """Get a specific category"""
    try:
        category = Category.query.get_or_404(category_id)
        return jsonify({
            'success': True,
            'category': category.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@category_bp.route('/categories', methods=['POST'])
def create_category():
    """Create a new category"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'success': False, 'error': 'اسم التصنيف مطلوب'}), 400
        
        # Check if category already exists
        existing_category = Category.query.filter_by(name=data['name']).first()
        if existing_category:
            return jsonify({'success': False, 'error': 'التصنيف موجود بالفعل'}), 400
        
        category = Category(
            name=data['name'],
            description=data.get('description'),
            icon_url=data.get('icon_url')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء التصنيف بنجاح',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@category_bp.route('/categories/<category_id>', methods=['PUT'])
def update_category(category_id):
    """Update a category"""
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'لا توجد بيانات للتحديث'}), 400
        
        # Check if new name already exists (if name is being changed)
        if 'name' in data and data['name'] != category.name:
            existing_category = Category.query.filter_by(name=data['name']).first()
            if existing_category:
                return jsonify({'success': False, 'error': 'اسم التصنيف موجود بالفعل'}), 400
        
        # Update fields
        if 'name' in data:
            category.name = data['name']
        if 'description' in data:
            category.description = data['description']
        if 'icon_url' in data:
            category.icon_url = data['icon_url']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث التصنيف بنجاح',
            'category': category.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@category_bp.route('/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Delete a category"""
    try:
        category = Category.query.get_or_404(category_id)
        
        # Check if category has content
        if hasattr(category, 'content_items') and len(category.content_items) > 0:
            return jsonify({
                'success': False, 
                'error': 'لا يمكن حذف التصنيف لأنه يحتوي على محتوى'
            }), 400
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم حذف التصنيف بنجاح'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

