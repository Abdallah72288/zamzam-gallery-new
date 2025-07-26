// Global variables
let selectedFiles = [];
let categories = [];
let types = [];
let brands = [];
let currentFilter = 'all';

// API Base URL
const API_BASE = '/api';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    try {
        await loadCategories();
        await loadTypes();
        await loadBrands();
        await loadStats();
        await loadGallery();
        setupEventListeners();
        showNotification('تم تحميل التطبيق بنجاح', 'success');
    } catch (error) {
        console.error('Error initializing app:', error);
        showNotification('حدث خطأ في تحميل التطبيق', 'error');
    }
}

function setupEventListeners() {
    // File upload
    const fileInput = document.getElementById('file-input');
    const uploadArea = document.getElementById('upload-area');
    const uploadForm = document.getElementById('upload-form');

    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // Upload form
    uploadForm.addEventListener('submit', handleUploadSubmit);

    // Category change for types
    document.getElementById('upload-category').addEventListener('change', handleCategoryChange);

    // Gallery filters
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', handleFilterChange);
    });

    // Management tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', handleTabChange);
    });
}

// File handling functions
function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    processSelectedFiles(files);
}

function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
}

function handleDragLeave(event) {
    event.currentTarget.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    const files = Array.from(event.dataTransfer.files);
    processSelectedFiles(files);
}

function processSelectedFiles(files) {
    selectedFiles = files.filter(file => {
        const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'video/mp4', 'video/mov', 'video/avi', 'video/webm'];
        return validTypes.includes(file.type) && file.size <= 100 * 1024 * 1024; // 100MB limit
    });

    if (selectedFiles.length > 0) {
        document.getElementById('upload-form').style.display = 'block';
        updateUploadAreaText();
    } else {
        showNotification('يرجى اختيار ملفات صالحة (صور أو فيديوهات أقل من 100 ميجابايت)', 'error');
    }
}

function updateUploadAreaText() {
    const uploadArea = document.getElementById('upload-area');
    const icon = uploadArea.querySelector('.upload-icon i');
    const text = uploadArea.querySelector('.upload-text');
    const hint = uploadArea.querySelector('.upload-hint');

    icon.className = 'fas fa-check-circle';
    icon.style.color = 'var(--success-color)';
    text.textContent = `تم اختيار ${selectedFiles.length} ملف`;
    hint.textContent = 'انقر هنا لاختيار ملفات أخرى أو املأ النموذج أدناه';
}

async function handleUploadSubmit(event) {
    event.preventDefault();

    if (selectedFiles.length === 0) {
        showNotification('يرجى اختيار ملفات للرفع', 'error');
        return;
    }

    const categoryId = document.getElementById('upload-category').value;
    if (!categoryId) {
        showNotification('يرجى اختيار تصنيف', 'error');
        return;
    }

    const formData = new FormData();
    
    // Add files
    selectedFiles.forEach(file => {
        formData.append('files', file);
    });

    // Add metadata
    formData.append('title', document.getElementById('upload-title').value);
    formData.append('description', document.getElementById('upload-description').value);
    formData.append('category_id', categoryId);
    formData.append('type_id', document.getElementById('upload-type').value);
    formData.append('brand_id', document.getElementById('upload-brand').value);
    formData.append('tags', document.getElementById('upload-tags').value);
    formData.append('uploaded_by', 'default-user-id'); // Should come from authentication

    try {
        showUploadProgress(true);
        
        const response = await fetch(`${API_BASE}/content`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            showNotification(result.message, 'success');
            resetUploadForm();
            await loadStats();
            await loadGallery();
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showNotification('حدث خطأ أثناء رفع الملفات', 'error');
    } finally {
        showUploadProgress(false);
    }
}

function showUploadProgress(show) {
    const progressBar = document.getElementById('upload-progress');
    const submitBtn = document.querySelector('#upload-form button[type="submit"]');
    
    if (show) {
        progressBar.style.display = 'block';
        submitBtn.innerHTML = '<div class="loading"></div> جاري الرفع...';
        submitBtn.disabled = true;
        
        // Simulate progress
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            document.getElementById('progress-fill').style.width = progress + '%';
        }, 200);
        
        submitBtn.dataset.interval = interval;
    } else {
        progressBar.style.display = 'none';
        submitBtn.innerHTML = '<i class="fas fa-upload"></i> رفع الملفات';
        submitBtn.disabled = false;
        document.getElementById('progress-fill').style.width = '100%';
        
        if (submitBtn.dataset.interval) {
            clearInterval(submitBtn.dataset.interval);
        }
        
        setTimeout(() => {
            document.getElementById('progress-fill').style.width = '0%';
        }, 1000);
    }
}

function resetUploadForm() {
    selectedFiles = [];
    document.getElementById('upload-form').style.display = 'none';
    document.getElementById('upload-form').reset();
    
    // Reset upload area
    const uploadArea = document.getElementById('upload-area');
    const icon = uploadArea.querySelector('.upload-icon i');
    const text = uploadArea.querySelector('.upload-text');
    const hint = uploadArea.querySelector('.upload-hint');

    icon.className = 'fas fa-cloud-upload-alt';
    icon.style.color = '';
    text.textContent = 'اسحب الملفات هنا أو انقر للاختيار';
    hint.textContent = 'يدعم: JPG, PNG, GIF, MP4, MOV, AVI (حتى 100 ميجابايت)';
}

function cancelUpload() {
    resetUploadForm();
}

// Data loading functions
async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE}/categories`);
        const result = await response.json();
        
        if (result.success) {
            categories = result.categories;
            populateCategorySelect();
            populateCategoriesList();
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function loadTypes() {
    try {
        const response = await fetch(`${API_BASE}/types`);
        const result = await response.json();
        
        if (result.success) {
            types = result.types;
            populateTypesList();
        }
    } catch (error) {
        console.error('Error loading types:', error);
    }
}

async function loadBrands() {
    try {
        const response = await fetch(`${API_BASE}/brands`);
        const result = await response.json();
        
        if (result.success) {
            brands = result.brands;
            populateBrandSelect();
            populateBrandsList();
        }
    } catch (error) {
        console.error('Error loading brands:', error);
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/content/stats`);
        const result = await response.json();
        
        if (result.success) {
            const stats = result.stats;
            document.getElementById('total-images').textContent = stats.total_images;
            document.getElementById('total-videos').textContent = stats.total_videos;
            document.getElementById('total-views').textContent = stats.total_views;
            document.getElementById('total-storage').textContent = '0 MB'; // Calculate from file sizes
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadGallery() {
    try {
        const response = await fetch(`${API_BASE}/content?content_type=${currentFilter === 'all' ? '' : currentFilter}`);
        const result = await response.json();
        
        if (result.success) {
            populateGallery(result.content);
        }
    } catch (error) {
        console.error('Error loading gallery:', error);
    }
}

// UI population functions
function populateCategorySelect() {
    const select = document.getElementById('upload-category');
    select.innerHTML = '<option value="">اختر تصنيف</option>';
    
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.id;
        option.textContent = category.name;
        select.appendChild(option);
    });
}

function populateTypeSelect(categoryId = null) {
    const select = document.getElementById('upload-type');
    select.innerHTML = '<option value="">اختر نوع (اختياري)</option>';
    
    const filteredTypes = categoryId ? 
        types.filter(type => type.category_id === categoryId) : 
        types;
    
    filteredTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type.id;
        option.textContent = type.name;
        select.appendChild(option);
    });
}

function populateBrandSelect() {
    const select = document.getElementById('upload-brand');
    select.innerHTML = '<option value="">اختر علامة تجارية (اختياري)</option>';
    
    brands.forEach(brand => {
        const option = document.createElement('option');
        option.value = brand.id;
        option.textContent = brand.name;
        select.appendChild(option);
    });
}

function populateGallery(content) {
    const grid = document.getElementById('gallery-grid');
    
    if (content.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-images"></i>
                <h3>لا توجد ملفات</h3>
                <p>لا توجد ملفات تطابق المرشح المحدد</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = content.map(item => `
        <div class="gallery-item" onclick="viewContent('${item.id}')">
            <div class="gallery-item-media">
                ${item.content_type === 'image' ? 
                    `<img src="${item.file_url}" alt="${item.title}" style="width: 100%; height: 100%; object-fit: cover;">` :
                    `<i class="fas fa-play-circle" style="font-size: 3rem; color: var(--primary-color);"></i>`
                }
            </div>
            <div class="gallery-item-content">
                <div class="gallery-item-title">${item.title}</div>
                <div class="gallery-item-meta">
                    <span><i class="fas fa-eye"></i> ${item.views_count}</span>
                    <span><i class="fas fa-heart"></i> ${item.likes_count}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function populateCategoriesList() {
    const list = document.getElementById('categories-list');
    
    if (categories.length === 0) {
        list.innerHTML = '<div class="empty-state"><p>لا توجد تصنيفات</p></div>';
        return;
    }
    
    list.innerHTML = categories.map(category => `
        <div class="management-item">
            <div class="management-item-info">
                <h4>${category.name}</h4>
                <p>${category.description || 'لا يوجد وصف'}</p>
            </div>
            <div class="management-item-actions">
                <button class="btn btn-secondary btn-small" onclick="editItem('category', '${category.id}')">
                    <i class="fas fa-edit"></i> تعديل
                </button>
                <button class="btn btn-danger btn-small" onclick="deleteItem('category', '${category.id}', '${category.name}')">
                    <i class="fas fa-trash"></i> حذف
                </button>
            </div>
        </div>
    `).join('');
}

function populateTypesList() {
    const list = document.getElementById('types-list');
    
    if (types.length === 0) {
        list.innerHTML = '<div class="empty-state"><p>لا توجد أنواع</p></div>';
        return;
    }
    
    list.innerHTML = types.map(type => `
        <div class="management-item">
            <div class="management-item-info">
                <h4>${type.name}</h4>
                <p>التصنيف: ${type.category_name} | ${type.description || 'لا يوجد وصف'}</p>
            </div>
            <div class="management-item-actions">
                <button class="btn btn-secondary btn-small" onclick="editItem('type', '${type.id}')">
                    <i class="fas fa-edit"></i> تعديل
                </button>
                <button class="btn btn-danger btn-small" onclick="deleteItem('type', '${type.id}', '${type.name}')">
                    <i class="fas fa-trash"></i> حذف
                </button>
            </div>
        </div>
    `).join('');
}

function populateBrandsList() {
    const list = document.getElementById('brands-list');
    
    if (brands.length === 0) {
        list.innerHTML = '<div class="empty-state"><p>لا توجد علامات تجارية</p></div>';
        return;
    }
    
    list.innerHTML = brands.map(brand => `
        <div class="management-item">
            <div class="management-item-info">
                <h4>${brand.name}</h4>
                <p>${brand.description || 'لا يوجد وصف'}</p>
            </div>
            <div class="management-item-actions">
                <button class="btn btn-secondary btn-small" onclick="editItem('brand', '${brand.id}')">
                    <i class="fas fa-edit"></i> تعديل
                </button>
                <button class="btn btn-danger btn-small" onclick="deleteItem('brand', '${brand.id}', '${brand.name}')">
                    <i class="fas fa-trash"></i> حذف
                </button>
            </div>
        </div>
    `).join('');
}

// Event handlers
function handleCategoryChange(event) {
    const categoryId = event.target.value;
    populateTypeSelect(categoryId);
}

function handleFilterChange(event) {
    // Remove active class from all buttons
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Update current filter
    currentFilter = event.target.dataset.filter;
    
    // Reload gallery
    loadGallery();
}

function handleTabChange(event) {
    // Remove active class from all tabs
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to clicked tab
    event.target.classList.add('active');
    
    // Show corresponding content
    const tabId = event.target.dataset.tab + '-tab';
    document.getElementById(tabId).classList.add('active');
}

// Management functions
function showAddForm(type) {
    const name = prompt(`أدخل اسم ${getTypeLabel(type)} الجديد:`);
    if (!name) return;
    
    const description = prompt('أدخل الوصف (اختياري):') || '';
    
    let categoryId = null;
    if (type === 'type') {
        const categoryName = prompt('أدخل اسم التصنيف:');
        const category = categories.find(cat => cat.name === categoryName);
        if (!category) {
            showNotification('التصنيف غير موجود', 'error');
            return;
        }
        categoryId = category.id;
    }
    
    addItem(type, { name, description, category_id: categoryId });
}

async function addItem(type, data) {
    try {
        const response = await fetch(`${API_BASE}/${type}s`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            
            // Reload data
            if (type === 'category') {
                await loadCategories();
            } else if (type === 'type') {
                await loadTypes();
            } else if (type === 'brand') {
                await loadBrands();
            }
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        console.error('Error adding item:', error);
        showNotification('حدث خطأ أثناء الإضافة', 'error');
    }
}

async function deleteItem(type, id, name) {
    if (!confirm(`هل أنت متأكد من حذف "${name}"؟`)) return;
    
    try {
        const response = await fetch(`${API_BASE}/${type}s/${id}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            
            // Reload data
            if (type === 'category') {
                await loadCategories();
            } else if (type === 'type') {
                await loadTypes();
            } else if (type === 'brand') {
                await loadBrands();
            }
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        console.error('Error deleting item:', error);
        showNotification('حدث خطأ أثناء الحذف', 'error');
    }
}

function editItem(type, id) {
    // Simple edit implementation
    const newName = prompt(`أدخل الاسم الجديد:`);
    if (!newName) return;
    
    const newDescription = prompt('أدخل الوصف الجديد (اختياري):') || '';
    
    updateItem(type, id, { name: newName, description: newDescription });
}

async function updateItem(type, id, data) {
    try {
        const response = await fetch(`${API_BASE}/${type}s/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
            
            // Reload data
            if (type === 'category') {
                await loadCategories();
            } else if (type === 'type') {
                await loadTypes();
            } else if (type === 'brand') {
                await loadBrands();
            }
        } else {
            showNotification(result.error, 'error');
        }
    } catch (error) {
        console.error('Error updating item:', error);
        showNotification('حدث خطأ أثناء التحديث', 'error');
    }
}

// Utility functions
function getTypeLabel(type) {
    const labels = {
        'category': 'التصنيف',
        'type': 'النوع',
        'brand': 'العلامة التجارية'
    };
    return labels[type] || type;
}

function viewContent(contentId) {
    // Simple content viewer - could be enhanced with a modal
    window.open(`${API_BASE}/content/${contentId}`, '_blank');
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

function showNotification(message, type = 'success') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create new notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Hide notification after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

