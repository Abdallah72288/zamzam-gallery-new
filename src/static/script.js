// Global variables
let currentFilter = 'all';
let currentManagementTab = 'categories';
let isDeveloperMode = false;
let currentTheme = 'light';
let selectedFiles = [];

// API Base URL
const API_BASE = '';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize application
async function initializeApp() {
    try {
        await loadSettings();
        await loadStats();
        await loadContent();
        await loadCategories();
        await loadTypes();
        await loadBrands();
        await loadSocialLinks();
        setupEventListeners();
        showNotification('تم تحميل التطبيق بنجاح', 'success');
    } catch (error) {
        console.error('Error initializing app:', error);
        showNotification('حدث خطأ في تحميل التطبيق', 'error');
    }
}

// Setup event listeners
function setupEventListeners() {
    // File input change
    document.getElementById('file-input').addEventListener('change', handleFileSelect);
    
    // Upload area drag and drop
    const uploadArea = document.querySelector('.upload-area');
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Form submissions
    document.getElementById('category-form').addEventListener('submit', handleCategorySubmit);
    document.getElementById('type-form').addEventListener('submit', handleTypeSubmit);
    document.getElementById('brand-form').addEventListener('submit', handleBrandSubmit);
    
    // Theme detection
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        setTheme('dark');
    }
}

// Load settings from server
async function loadSettings() {
    try {
        const response = await fetch(`${API_BASE}/api/settings`);
        if (response.ok) {
            const settings = await response.json();
            applySettings(settings);
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

// Apply settings to the interface
function applySettings(settings) {
    // Apply theme
    if (settings.theme) {
        setTheme(settings.theme);
    }
    
    // Apply colors
    if (settings.primary_color) {
        document.documentElement.style.setProperty('--primary-color', settings.primary_color);
    }
    
    // Apply font
    if (settings.font_family) {
        document.body.style.fontFamily = `'${settings.font_family}', 'Cairo', 'Tajawal', sans-serif`;
    }
    
    // Apply SEO settings
    if (settings.site_title) {
        document.title = settings.site_title;
    }
    
    if (settings.site_description) {
        const metaDesc = document.querySelector('meta[name="description"]');
        if (metaDesc) metaDesc.content = settings.site_description;
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/content/stats`);
        if (response.ok) {
            const stats = await response.json();
            updateStats(stats);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Update statistics display
function updateStats(stats) {
    document.getElementById('total-images').textContent = stats.total_images || 0;
    document.getElementById('total-videos').textContent = stats.total_videos || 0;
    document.getElementById('total-views').textContent = stats.total_views || 0;
    document.getElementById('storage-used').textContent = `${stats.storage_used || 0} MB`;
}

// Load content from server
async function loadContent() {
    try {
        const response = await fetch(`${API_BASE}/api/content`);
        if (response.ok) {
            const content = await response.json();
            displayContent(content);
        }
    } catch (error) {
        console.error('Error loading content:', error);
        showEmptyState();
    }
}

// Display content in gallery
function displayContent(content) {
    const galleryGrid = document.getElementById('gallery-grid');
    const emptyGallery = document.getElementById('empty-gallery');
    
    if (!content || content.length === 0) {
        showEmptyState();
        return;
    }
    
    galleryGrid.innerHTML = '';
    emptyGallery.style.display = 'none';
    
    content.forEach(item => {
        if (currentFilter === 'all' || currentFilter === item.content_type) {
            const galleryItem = createGalleryItem(item);
            galleryGrid.appendChild(galleryItem);
        }
    });
    
    if (galleryGrid.children.length === 0) {
        showEmptyState();
    }
}

// Create gallery item element
function createGalleryItem(item) {
    const div = document.createElement('div');
    div.className = 'gallery-item';
    div.onclick = () => openContentModal(item);
    
    const isVideo = item.content_type === 'video';
    const mediaElement = isVideo ? 
        `<video class="gallery-image" src="${item.file_path}" controls></video>` :
        `<img class="gallery-image" src="${item.file_path}" alt="${item.title}" loading="lazy">`;
    
    div.innerHTML = `
        ${mediaElement}
        <div class="gallery-info">
            <div class="gallery-title">${item.title}</div>
            <div class="gallery-meta">
                <span><i class="fas fa-${isVideo ? 'video' : 'image'}"></i> ${item.content_type}</span>
                <span><i class="fas fa-eye"></i> ${item.views || 0}</span>
            </div>
        </div>
    `;
    
    return div;
}

// Show empty state
function showEmptyState() {
    const galleryGrid = document.getElementById('gallery-grid');
    const emptyGallery = document.getElementById('empty-gallery');
    
    galleryGrid.innerHTML = '';
    emptyGallery.style.display = 'block';
}

// Load categories
async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE}/api/categories`);
        if (response.ok) {
            const categories = await response.json();
            updateCategoriesDisplay(categories);
            updateCategoriesSelects(categories);
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Update categories display
function updateCategoriesDisplay(categories) {
    const categoriesList = document.getElementById('categories-list');
    categoriesList.innerHTML = '';
    
    if (categories.length === 0) {
        categoriesList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">لا توجد تصنيفات</p>';
        return;
    }
    
    const table = document.createElement('table');
    table.className = 'management-table';
    table.innerHTML = `
        <thead>
            <tr>
                <th>الاسم</th>
                <th>الوصف</th>
                <th>عدد العناصر</th>
                <th>الإجراءات</th>
            </tr>
        </thead>
        <tbody>
            ${categories.map(category => `
                <tr>
                    <td>${category.name}</td>
                    <td>${category.description || '-'}</td>
                    <td>${category.content_count || 0}</td>
                    <td>
                        <button class="btn btn-secondary" onclick="editCategory(${category.id})">
                            <i class="fas fa-edit"></i> تعديل
                        </button>
                        <button class="btn btn-danger" onclick="deleteCategory(${category.id})">
                            <i class="fas fa-trash"></i> حذف
                        </button>
                    </td>
                </tr>
            `).join('')}
        </tbody>
    `;
    
    categoriesList.appendChild(table);
}

// Update categories in select elements
function updateCategoriesSelects(categories) {
    const selects = ['upload-category', 'type-category'];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select) {
            const currentValue = select.value;
            select.innerHTML = '<option value="">اختر التصنيف</option>';
            
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
                if (category.id == currentValue) option.selected = true;
                select.appendChild(option);
            });
        }
    });
}

// Load types
async function loadTypes() {
    try {
        const response = await fetch(`${API_BASE}/api/types`);
        if (response.ok) {
            const types = await response.json();
            updateTypesDisplay(types);
            updateTypesSelects(types);
        }
    } catch (error) {
        console.error('Error loading types:', error);
    }
}

// Update types display
function updateTypesDisplay(types) {
    const typesList = document.getElementById('types-list');
    typesList.innerHTML = '';
    
    if (types.length === 0) {
        typesList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">لا توجد أنواع</p>';
        return;
    }
    
    const table = document.createElement('table');
    table.className = 'management-table';
    table.innerHTML = `
        <thead>
            <tr>
                <th>الاسم</th>
                <th>التصنيف</th>
                <th>الوصف</th>
                <th>عدد العناصر</th>
                <th>الإجراءات</th>
            </tr>
        </thead>
        <tbody>
            ${types.map(type => `
                <tr>
                    <td>${type.name}</td>
                    <td>${type.category_name || '-'}</td>
                    <td>${type.description || '-'}</td>
                    <td>${type.content_count || 0}</td>
                    <td>
                        <button class="btn btn-secondary" onclick="editType(${type.id})">
                            <i class="fas fa-edit"></i> تعديل
                        </button>
                        <button class="btn btn-danger" onclick="deleteType(${type.id})">
                            <i class="fas fa-trash"></i> حذف
                        </button>
                    </td>
                </tr>
            `).join('')}
        </tbody>
    `;
    
    typesList.appendChild(table);
}

// Update types in select elements
function updateTypesSelects(types) {
    const select = document.getElementById('upload-type');
    if (select) {
        const currentValue = select.value;
        select.innerHTML = '<option value="">اختر النوع</option>';
        
        types.forEach(type => {
            const option = document.createElement('option');
            option.value = type.id;
            option.textContent = type.name;
            if (type.id == currentValue) option.selected = true;
            select.appendChild(option);
        });
    }
}

// Load brands
async function loadBrands() {
    try {
        const response = await fetch(`${API_BASE}/api/brands`);
        if (response.ok) {
            const brands = await response.json();
            updateBrandsDisplay(brands);
            updateBrandsSelects(brands);
        }
    } catch (error) {
        console.error('Error loading brands:', error);
    }
}

// Update brands display
function updateBrandsDisplay(brands) {
    const brandsList = document.getElementById('brands-list');
    brandsList.innerHTML = '';
    
    if (brands.length === 0) {
        brandsList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">لا توجد علامات تجارية</p>';
        return;
    }
    
    const table = document.createElement('table');
    table.className = 'management-table';
    table.innerHTML = `
        <thead>
            <tr>
                <th>الاسم</th>
                <th>الوصف</th>
                <th>عدد العناصر</th>
                <th>الإجراءات</th>
            </tr>
        </thead>
        <tbody>
            ${brands.map(brand => `
                <tr>
                    <td>${brand.name}</td>
                    <td>${brand.description || '-'}</td>
                    <td>${brand.content_count || 0}</td>
                    <td>
                        <button class="btn btn-secondary" onclick="editBrand(${brand.id})">
                            <i class="fas fa-edit"></i> تعديل
                        </button>
                        <button class="btn btn-danger" onclick="deleteBrand(${brand.id})">
                            <i class="fas fa-trash"></i> حذف
                        </button>
                    </td>
                </tr>
            `).join('')}
        </tbody>
    `;
    
    brandsList.appendChild(table);
}

// Update brands in select elements
function updateBrandsSelects(brands) {
    const select = document.getElementById('upload-brand');
    if (select) {
        const currentValue = select.value;
        select.innerHTML = '<option value="">اختر العلامة التجارية</option>';
        
        brands.forEach(brand => {
            const option = document.createElement('option');
            option.value = brand.id;
            option.textContent = brand.name;
            if (brand.id == currentValue) option.selected = true;
            select.appendChild(option);
        });
    }
}

// Load social media links
async function loadSocialLinks() {
    try {
        const response = await fetch(`${API_BASE}/api/settings/social`);
        if (response.ok) {
            const socialLinks = await response.json();
            updateSocialLinksDisplay(socialLinks);
        }
    } catch (error) {
        console.error('Error loading social links:', error);
        // Show default social links
        updateSocialLinksDisplay({});
    }
}

// Update social media links display
function updateSocialLinksDisplay(socialLinks) {
    const socialLinksContainer = document.getElementById('social-links');
    socialLinksContainer.innerHTML = '';
    
    const defaultSocials = [
        { key: 'facebook', icon: 'fab fa-facebook-f', name: 'Facebook' },
        { key: 'twitter', icon: 'fab fa-twitter', name: 'Twitter' },
        { key: 'instagram', icon: 'fab fa-instagram', name: 'Instagram' },
        { key: 'linkedin', icon: 'fab fa-linkedin-in', name: 'LinkedIn' },
        { key: 'youtube', icon: 'fab fa-youtube', name: 'YouTube' },
        { key: 'github', icon: 'fab fa-github', name: 'GitHub' },
        { key: 'telegram', icon: 'fab fa-telegram-plane', name: 'Telegram' },
        { key: 'whatsapp', icon: 'fab fa-whatsapp', name: 'WhatsApp' }
    ];
    
    defaultSocials.forEach(social => {
        const link = socialLinks[social.key];
        if (link) {
            const a = document.createElement('a');
            a.href = link;
            a.className = 'social-link';
            a.target = '_blank';
            a.rel = 'noopener noreferrer';
            a.title = social.name;
            a.innerHTML = `<i class="${social.icon}"></i>`;
            socialLinksContainer.appendChild(a);
        }
    });
}

// Tab management
function showTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all nav tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab
    const selectedTab = document.getElementById(`${tabName}-tab`) || document.getElementById(`${tabName}-tab-content`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Add active class to clicked nav tab
    event.target.classList.add('active');
    
    // Load content based on tab
    if (tabName === 'gallery') {
        loadContent();
    } else if (tabName === 'management') {
        loadCategories();
        loadTypes();
        loadBrands();
    }
}

// Management tab management
function showManagementTab(tabName) {
    currentManagementTab = tabName;
    
    // Hide all management tab contents
    document.querySelectorAll('#management-tab-content .tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from management nav tabs
    document.querySelectorAll('#management-tab-content .nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected management tab
    const selectedTab = document.getElementById(`${tabName}-management`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Add active class to clicked nav tab
    event.target.classList.add('active');
}

// Developer mode functions
function toggleDeveloperMode() {
    isDeveloperMode = !isDeveloperMode;
    const managementTab = document.getElementById('management-tab');
    const developerModal = document.getElementById('developer-modal');
    
    if (isDeveloperMode) {
        managementTab.style.display = 'block';
        developerModal.classList.add('active');
        showNotification('تم تفعيل وضع المطور', 'info');
    } else {
        managementTab.style.display = 'none';
        developerModal.classList.remove('active');
        showNotification('تم إلغاء تفعيل وضع المطور', 'info');
    }
}

function closeDeveloperModal() {
    document.getElementById('developer-modal').classList.remove('active');
}

function showDeveloperTab(tabName) {
    // Hide all developer tab contents
    document.querySelectorAll('#developer-modal .tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from developer nav tabs
    document.querySelectorAll('#developer-modal .nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected developer tab
    const selectedTab = document.getElementById(`${tabName}-settings`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Add active class to clicked nav tab
    event.target.classList.add('active');
}

// Theme management
function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(currentTheme);
}

function setTheme(theme) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
    
    const themeSwitch = document.getElementById('theme-mode-switch');
    if (themeSwitch) {
        themeSwitch.checked = theme === 'dark';
    }
}

// File handling
function handleFileSelect(event) {
    selectedFiles = Array.from(event.target.files);
    if (selectedFiles.length > 0) {
        showUploadForm();
    }
}

function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    
    selectedFiles = Array.from(event.dataTransfer.files);
    if (selectedFiles.length > 0) {
        showUploadForm();
    }
}

function showUploadForm() {
    document.getElementById('upload-form').style.display = 'block';
}

function cancelUpload() {
    selectedFiles = [];
    document.getElementById('upload-form').style.display = 'none';
    document.getElementById('file-input').value = '';
}

// Upload files
async function uploadFiles() {
    if (selectedFiles.length === 0) {
        showNotification('يرجى اختيار ملفات للرفع', 'warning');
        return;
    }
    
    const title = document.getElementById('upload-title').value.trim();
    const description = document.getElementById('upload-description').value.trim();
    const categoryId = document.getElementById('upload-category').value;
    const typeId = document.getElementById('upload-type').value;
    const brandId = document.getElementById('upload-brand').value;
    const tags = document.getElementById('upload-tags').value.trim();
    
    if (!title) {
        showNotification('يرجى إدخال عنوان للملف', 'warning');
        return;
    }
    
    if (!categoryId) {
        showNotification('يرجى اختيار تصنيف', 'warning');
        return;
    }
    
    const progressContainer = document.getElementById('upload-progress');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    progressContainer.style.display = 'block';
    
    try {
        for (let i = 0; i < selectedFiles.length; i++) {
            const file = selectedFiles[i];
            const formData = new FormData();
            
            formData.append('file', file);
            formData.append('title', title);
            formData.append('description', description);
            formData.append('category_id', categoryId);
            if (typeId) formData.append('type_id', typeId);
            if (brandId) formData.append('brand_id', brandId);
            if (tags) formData.append('tags', tags);
            
            const response = await fetch(`${API_BASE}/api/content/upload`, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const progress = ((i + 1) / selectedFiles.length) * 100;
                progressFill.style.width = `${progress}%`;
                progressText.textContent = `تم رفع ${i + 1} من ${selectedFiles.length} ملف`;
            } else {
                throw new Error('فشل في رفع الملف');
            }
        }
        
        showNotification('تم رفع جميع الملفات بنجاح', 'success');
        cancelUpload();
        await loadContent();
        await loadStats();
        
    } catch (error) {
        console.error('Upload error:', error);
        showNotification('حدث خطأ أثناء رفع الملفات', 'error');
    } finally {
        progressContainer.style.display = 'none';
    }
}

// Filter content
function filterContent(type) {
    currentFilter = type;
    
    // Update active filter button
    document.querySelectorAll('#gallery-tab .nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');
    
    loadContent();
}

// Category management
function showAddCategoryModal() {
    document.getElementById('category-modal-title').textContent = 'إضافة تصنيف جديد';
    document.getElementById('category-form').reset();
    document.getElementById('category-id').value = '';
    document.getElementById('category-modal').classList.add('active');
}

function editCategory(id) {
    // Load category data and show edit modal
    fetch(`${API_BASE}/api/categories/${id}`)
        .then(response => response.json())
        .then(category => {
            document.getElementById('category-modal-title').textContent = 'تعديل التصنيف';
            document.getElementById('category-id').value = category.id;
            document.getElementById('category-name').value = category.name;
            document.getElementById('category-description').value = category.description || '';
            document.getElementById('category-modal').classList.add('active');
        })
        .catch(error => {
            console.error('Error loading category:', error);
            showNotification('حدث خطأ في تحميل بيانات التصنيف', 'error');
        });
}

function closeCategoryModal() {
    document.getElementById('category-modal').classList.remove('active');
}

async function handleCategorySubmit(event) {
    event.preventDefault();
    
    const id = document.getElementById('category-id').value;
    const name = document.getElementById('category-name').value.trim();
    const description = document.getElementById('category-description').value.trim();
    
    if (!name) {
        showNotification('يرجى إدخال اسم التصنيف', 'warning');
        return;
    }
    
    const data = { name, description };
    const url = id ? `${API_BASE}/api/categories/${id}` : `${API_BASE}/api/categories`;
    const method = id ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showNotification(id ? 'تم تحديث التصنيف بنجاح' : 'تم إضافة التصنيف بنجاح', 'success');
            closeCategoryModal();
            await loadCategories();
        } else {
            throw new Error('فشل في حفظ التصنيف');
        }
    } catch (error) {
        console.error('Error saving category:', error);
        showNotification('حدث خطأ في حفظ التصنيف', 'error');
    }
}

async function deleteCategory(id) {
    if (!confirm('هل أنت متأكد من حذف هذا التصنيف؟')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/categories/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('تم حذف التصنيف بنجاح', 'success');
            await loadCategories();
        } else {
            throw new Error('فشل في حذف التصنيف');
        }
    } catch (error) {
        console.error('Error deleting category:', error);
        showNotification('حدث خطأ في حذف التصنيف', 'error');
    }
}

// Type management
function showAddTypeModal() {
    document.getElementById('type-modal-title').textContent = 'إضافة نوع جديد';
    document.getElementById('type-form').reset();
    document.getElementById('type-id').value = '';
    document.getElementById('type-modal').classList.add('active');
}

function editType(id) {
    fetch(`${API_BASE}/api/types/${id}`)
        .then(response => response.json())
        .then(type => {
            document.getElementById('type-modal-title').textContent = 'تعديل النوع';
            document.getElementById('type-id').value = type.id;
            document.getElementById('type-category').value = type.category_id;
            document.getElementById('type-name').value = type.name;
            document.getElementById('type-description').value = type.description || '';
            document.getElementById('type-modal').classList.add('active');
        })
        .catch(error => {
            console.error('Error loading type:', error);
            showNotification('حدث خطأ في تحميل بيانات النوع', 'error');
        });
}

function closeTypeModal() {
    document.getElementById('type-modal').classList.remove('active');
}

async function handleTypeSubmit(event) {
    event.preventDefault();
    
    const id = document.getElementById('type-id').value;
    const categoryId = document.getElementById('type-category').value;
    const name = document.getElementById('type-name').value.trim();
    const description = document.getElementById('type-description').value.trim();
    
    if (!name || !categoryId) {
        showNotification('يرجى إدخال جميع البيانات المطلوبة', 'warning');
        return;
    }
    
    const data = { category_id: categoryId, name, description };
    const url = id ? `${API_BASE}/api/types/${id}` : `${API_BASE}/api/types`;
    const method = id ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showNotification(id ? 'تم تحديث النوع بنجاح' : 'تم إضافة النوع بنجاح', 'success');
            closeTypeModal();
            await loadTypes();
        } else {
            throw new Error('فشل في حفظ النوع');
        }
    } catch (error) {
        console.error('Error saving type:', error);
        showNotification('حدث خطأ في حفظ النوع', 'error');
    }
}

async function deleteType(id) {
    if (!confirm('هل أنت متأكد من حذف هذا النوع؟')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/types/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('تم حذف النوع بنجاح', 'success');
            await loadTypes();
        } else {
            throw new Error('فشل في حذف النوع');
        }
    } catch (error) {
        console.error('Error deleting type:', error);
        showNotification('حدث خطأ في حذف النوع', 'error');
    }
}

// Brand management
function showAddBrandModal() {
    document.getElementById('brand-modal-title').textContent = 'إضافة علامة تجارية جديدة';
    document.getElementById('brand-form').reset();
    document.getElementById('brand-id').value = '';
    document.getElementById('brand-modal').classList.add('active');
}

function editBrand(id) {
    fetch(`${API_BASE}/api/brands/${id}`)
        .then(response => response.json())
        .then(brand => {
            document.getElementById('brand-modal-title').textContent = 'تعديل العلامة التجارية';
            document.getElementById('brand-id').value = brand.id;
            document.getElementById('brand-name').value = brand.name;
            document.getElementById('brand-description').value = brand.description || '';
            document.getElementById('brand-modal').classList.add('active');
        })
        .catch(error => {
            console.error('Error loading brand:', error);
            showNotification('حدث خطأ في تحميل بيانات العلامة التجارية', 'error');
        });
}

function closeBrandModal() {
    document.getElementById('brand-modal').classList.remove('active');
}

async function handleBrandSubmit(event) {
    event.preventDefault();
    
    const id = document.getElementById('brand-id').value;
    const name = document.getElementById('brand-name').value.trim();
    const description = document.getElementById('brand-description').value.trim();
    
    if (!name) {
        showNotification('يرجى إدخال اسم العلامة التجارية', 'warning');
        return;
    }
    
    const data = { name, description };
    const url = id ? `${API_BASE}/api/brands/${id}` : `${API_BASE}/api/brands`;
    const method = id ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showNotification(id ? 'تم تحديث العلامة التجارية بنجاح' : 'تم إضافة العلامة التجارية بنجاح', 'success');
            closeBrandModal();
            await loadBrands();
        } else {
            throw new Error('فشل في حفظ العلامة التجارية');
        }
    } catch (error) {
        console.error('Error saving brand:', error);
        showNotification('حدث خطأ في حفظ العلامة التجارية', 'error');
    }
}

async function deleteBrand(id) {
    if (!confirm('هل أنت متأكد من حذف هذه العلامة التجارية؟')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/brands/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('تم حذف العلامة التجارية بنجاح', 'success');
            await loadBrands();
        } else {
            throw new Error('فشل في حذف العلامة التجارية');
        }
    } catch (error) {
        console.error('Error deleting brand:', error);
        showNotification('حدث خطأ في حذف العلامة التجارية', 'error');
    }
}

// Settings management
async function saveThemeSettings() {
    const theme = document.getElementById('theme-mode-switch').checked ? 'dark' : 'light';
    const primaryColor = document.getElementById('primary-color-picker').value;
    const fontFamily = document.getElementById('font-family-select').value;
    
    const settings = {
        theme,
        primary_color: primaryColor,
        font_family: fontFamily
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/settings/theme`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        
        if (response.ok) {
            showNotification('تم حفظ إعدادات السمة بنجاح', 'success');
            applySettings(settings);
        } else {
            throw new Error('فشل في حفظ الإعدادات');
        }
    } catch (error) {
        console.error('Error saving theme settings:', error);
        showNotification('حدث خطأ في حفظ إعدادات السمة', 'error');
    }
}

async function saveSocialSettings() {
    const socialSettings = {
        facebook: document.getElementById('social-facebook').value,
        twitter: document.getElementById('social-twitter').value,
        instagram: document.getElementById('social-instagram').value,
        linkedin: document.getElementById('social-linkedin').value,
        youtube: document.getElementById('social-youtube').value,
        github: document.getElementById('social-github').value,
        telegram: document.getElementById('social-telegram').value,
        whatsapp: document.getElementById('social-whatsapp').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/settings/social`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(socialSettings)
        });
        
        if (response.ok) {
            showNotification('تم حفظ روابط التواصل الاجتماعي بنجاح', 'success');
            await loadSocialLinks();
        } else {
            throw new Error('فشل في حفظ الروابط');
        }
    } catch (error) {
        console.error('Error saving social settings:', error);
        showNotification('حدث خطأ في حفظ روابط التواصل', 'error');
    }
}

async function saveSeoSettings() {
    const seoSettings = {
        site_title: document.getElementById('seo-title').value,
        site_description: document.getElementById('seo-description').value,
        site_keywords: document.getElementById('seo-keywords').value,
        site_author: document.getElementById('seo-author').value,
        site_url: document.getElementById('seo-url').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/settings/seo`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(seoSettings)
        });
        
        if (response.ok) {
            showNotification('تم حفظ إعدادات SEO بنجاح', 'success');
            applySettings(seoSettings);
        } else {
            throw new Error('فشل في حفظ الإعدادات');
        }
    } catch (error) {
        console.error('Error saving SEO settings:', error);
        showNotification('حدث خطأ في حفظ إعدادات SEO', 'error');
    }
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Hide notification after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 5000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        case 'info': return 'info-circle';
        default: return 'info-circle';
    }
}

// Content modal (for viewing full content)
function openContentModal(item) {
    // Increment view count
    fetch(`${API_BASE}/api/content/${item.id}/view`, { method: 'POST' })
        .catch(error => console.error('Error updating view count:', error));
    
    // Create and show modal
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 800px;">
            <div class="modal-header">
                <h3 class="modal-title">${item.title}</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
            </div>
            <div style="text-align: center; margin-bottom: 20px;">
                ${item.content_type === 'video' ? 
                    `<video src="${item.file_path}" controls style="max-width: 100%; max-height: 400px;"></video>` :
                    `<img src="${item.file_path}" alt="${item.title}" style="max-width: 100%; max-height: 400px; object-fit: contain;">`
                }
            </div>
            ${item.description ? `<p style="margin-bottom: 15px;">${item.description}</p>` : ''}
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 14px; color: var(--text-secondary);">
                <span><i class="fas fa-eye"></i> ${(item.views || 0) + 1} مشاهدة</span>
                <span><i class="fas fa-calendar"></i> ${new Date(item.created_at).toLocaleDateString('ar-SA')}</span>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

