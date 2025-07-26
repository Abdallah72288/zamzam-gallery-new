from flask import Blueprint, request, jsonify
from src.models.content import Content, db
from src.models.category import Category
from src.models.type import Type
from src.models.brand import Brand
from src.models.user import User
import os
import uuid
from werkzeug.utils import secure_filename

content_bp = Blueprint('content', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@content_bp.route('/content', methods=['GET'])
def get_all_content():
    """Get all content with optional filtering"""
    try:
        # Get query parameters
        category_id = request.args.get('category_id')
        type_id = request.args.get('type_id')
        brand_id = request.args.get('brand_id')
        content_type = request.args.get('content_type')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Build query
        query = Content.query.filter_by(is_public=True)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        if type_id:
            query = query.filter_by(type_id=type_id)
        if brand_id:
            query = query.filter_by(brand_id=brand_id)
        if content_type:
            query = query.filter_by(content_type=content_type)
        if search:
            query = query.filter(Content.title.contains(search))
        
        # Order by upload date (newest first)
        query = query.order_by(Content.upload_date.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        content_items = pagination.items
        
        return jsonify({
            'success': True,
            'content': [item.to_dict() for item in content_items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@content_bp.route('/content/<content_id>', methods=['GET'])
def get_content(content_id):
    """Get a specific content item"""
    try:
        content = Content.query.get_or_404(content_id)
        
        # Increment views
        content.increment_views()
        
        return jsonify({
            'success': True,
            'content': content.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@content_bp.route('/content', methods=['POST'])
def create_content():
    """Create new content (upload files)"""
    try:
        # Check if files are present
        if 'files' not in request.files:
            return jsonify({'success': False, 'error': 'لا توجد ملفات للرفع'}), 400
        
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({'success': False, 'error': 'لم يتم اختيار أي ملفات'}), 400
        
        # Get form data
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        category_id = request.form.get('category_id')
        type_id = request.form.get('type_id')
        brand_id = request.form.get('brand_id')
        tags = request.form.get('tags', '').split(',') if request.form.get('tags') else []
        uploaded_by = request.form.get('uploaded_by', 'default-user-id')  # Should come from authentication
        
        if not category_id:
            return jsonify({'success': False, 'error': 'يجب اختيار تصنيف'}), 400
        
        uploaded_content = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # Secure filename
                filename = secure_filename(file.filename)
                file_extension = filename.rsplit('.', 1)[1].lower()
                
                # Generate unique filename
                unique_filename = f"{uuid.uuid4()}.{file_extension}"
                
                # Create uploads directory if it doesn't exist
                upload_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save file
                file_path = os.path.join(upload_dir, unique_filename)
                file.save(file_path)
                
                # Determine content type
                content_type = 'image' if file_extension in ['png', 'jpg', 'jpeg', 'gif'] else 'video'
                
                # Create file URL (relative to static folder)
                file_url = f"/uploads/{unique_filename}"
                
                # For videos, we'll use the same file as thumbnail for now
                # In a real application, you'd generate a thumbnail
                thumbnail_url = file_url if content_type == 'image' else None
                
                # Create content record
                content = Content(
                    title=title or filename,
                    description=description,
                    file_url=file_url,
                    thumbnail_url=thumbnail_url,
                    content_type=content_type,
                    category_id=category_id,
                    type_id=type_id if type_id else None,
                    brand_id=brand_id if brand_id else None,
                    uploaded_by=uploaded_by,
                    tags=tags
                )
                
                db.session.add(content)
                uploaded_content.append(content)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'تم رفع {len(uploaded_content)} ملف بنجاح',
            'content': [item.to_dict() for item in uploaded_content]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@content_bp.route('/content/<content_id>', methods=['PUT'])
def update_content(content_id):
    """Update content metadata"""
    try:
        content = Content.query.get_or_404(content_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'title' in data:
            content.title = data['title']
        if 'description' in data:
            content.description = data['description']
        if 'category_id' in data:
            content.category_id = data['category_id']
        if 'type_id' in data:
            content.type_id = data['type_id']
        if 'brand_id' in data:
            content.brand_id = data['brand_id']
        if 'tags' in data:
            content.set_tags(data['tags'])
        if 'is_public' in data:
            content.is_public = data['is_public']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم تحديث المحتوى بنجاح',
            'content': content.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@content_bp.route('/content/<content_id>', methods=['DELETE'])
def delete_content(content_id):
    """Delete content"""
    try:
        content = Content.query.get_or_404(content_id)
        
        # Delete file from filesystem
        if content.file_url:
            file_path = os.path.join(os.path.dirname(__file__), '..', 'static', content.file_url.lstrip('/'))
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(content)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم حذف المحتوى بنجاح'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@content_bp.route('/content/<content_id>/like', methods=['POST'])
def like_content(content_id):
    """Like content"""
    try:
        content = Content.query.get_or_404(content_id)
        content.increment_likes()
        
        return jsonify({
            'success': True,
            'message': 'تم الإعجاب بالمحتوى',
            'likes_count': content.likes_count
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@content_bp.route('/content/stats', methods=['GET'])
def get_content_stats():
    """Get content statistics"""
    try:
        total_content = Content.query.count()
        total_images = Content.query.filter_by(content_type='image').count()
        total_videos = Content.query.filter_by(content_type='video').count()
        total_views = db.session.query(db.func.sum(Content.views_count)).scalar() or 0
        total_likes = db.session.query(db.func.sum(Content.likes_count)).scalar() or 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_content': total_content,
                'total_images': total_images,
                'total_videos': total_videos,
                'total_views': total_views,
                'total_likes': total_likes
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

