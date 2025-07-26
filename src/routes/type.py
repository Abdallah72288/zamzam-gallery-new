from flask import Blueprint, request, jsonify
from src.models.type import Type, db
from src.models.category import Category

type_bp = Blueprint('type', __name__)

@type_bp.route('/types', methods=['GET'])
def get_all_types():
    """Get all types with optional category filtering"""
    try:
        category_id = request.args.get('category_id')
        
        if category_id:
            types = Type.query.filter_by(category_id=category_id).all()
        else:
            types = Type.query.all()
        
        return jsonify({
            'success': True,
            'types': [type_obj.to_dict() for type_obj in types]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@type_bp.route('/types/<type_id>', methods=['GET'])
def get_type(type_id):
    """Get a specific type"""
    try:
        type_obj = Type.query.get_or_404(type_id)
        return jsonify({
            'success': True,
            'type': type_obj.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@type_bp.route('/types', methods=['POST'])
def create_type():
    """Create a new type"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'category_id' not in data:
            return jsonify({'success': False, 'error': 'اسم النوع ومعرف التصنيف مطلوبان'}), 400
        
        # Check if category exists
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({'success': False, 'error': 'التصنيف غير موجود'}), 400
        
        # Check if type already exists in this category
        existing_type = Type.query.filter_by(
            name=data['name'], 
            category_id=data['category_id']
        ).first()
        if existing_type:
            return jsonify({'success': False, 'error': 'النوع موجود بالفعل في هذا التصنيف'}), 400
        
        type_obj = Type(
            name=data['name'],
            category_id=data['category_id'],
            description=data.get('description')
        )
        
        db.session.add(type_obj)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء النوع بنجاح',
            'type': type_obj.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@type_bp.route('/types/<type_id>', methods=['PUT'])
def update_type(type_id):
    """Update a type"""
    try:
        type_obj = Type.query.get_or_404(type_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'لا توجد بيانات للتحديث'}), 400
        
        # Check if new name already exists in the same category (if name is being changed)
        if 'name' in data and data['name'] != type_obj.name:
            existing_type = Type.query.filter_by(
                name=data['name'], 
                category_id=type_obj.category_id
            ).first()
            if existing_type:
                return jsonify({'success': False, 'error': 'اسم النوع موجود بالفعل في هذا التصنيف'}), 400
        
        # Check if category is being changed and if it exists
        if 'category_id' in data and data['category_id'] != type_obj.category_id:
            category = Category.query.get(data['category_id'])
            if not category:
                return jsonify({'success': False, 'error': 'التصنيف الجديد غير موجود'}), 400
            
            # Check if type name already exists in the new category
            existing_type = Type.query.filter_by(
                name=type_obj.name, 
                category_id=data['category_id']
            ).first()
            if existing_type:
                return jsonify({'success': False, 'error': 'اسم النوع موجود بالفعل في التصنيف الجديد'}), 400
        
        # Update fields
        if 'name' in data:
            type_obj.name = data['name']
        if 'category_id' in data:
            type_obj.category_id = data['category_id']
        if 'description' in data:
            type_obj.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث النوع بنجاح',
            'type': type_obj.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@type_bp.route('/types/<type_id>', methods=['DELETE'])
def delete_type(type_id):
    """Delete a type"""
    try:
        type_obj = Type.query.get_or_404(type_id)
        
        # Check if type has content
        if hasattr(type_obj, 'content_items') and len(type_obj.content_items) > 0:
            return jsonify({
                'success': False, 
                'error': 'لا يمكن حذف النوع لأنه يحتوي على محتوى'
            }), 400
        
        db.session.delete(type_obj)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم حذف النوع بنجاح'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

