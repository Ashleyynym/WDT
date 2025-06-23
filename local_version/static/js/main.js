// Placeholder for any JS functionality (dropdowns, charts, AJAX calls, etc.)
console.log("WDT Air Cargo System JS loaded.");

// Container Tracking Platform - Main JavaScript

// Timeline Component
class Timeline {
    constructor(container, data) {
        this.container = container;
        this.data = data;
        this.init();
    }

    init() {
        this.render();
        this.bindEvents();
    }

    render() {
        const timelineHtml = this.data.map(item => `
            <div class="dot ${item.status}" data-tooltip="${item.tooltip}"></div>
        `).join('');
        
        this.container.innerHTML = `
            <div class="timeline">
                ${timelineHtml}
            </div>
        `;
    }

    bindEvents() {
        const dots = this.container.querySelectorAll('.dot');
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                this.showJourneyDetails(this.data[index]);
            });
        });
    }

    showJourneyDetails(item) {
        const drawer = new JourneyDrawer();
        drawer.show(item);
    }
}

// Journey Detail Drawer
class JourneyDrawer {
    constructor() {
        this.drawer = null;
        this.init();
    }

    init() {
        this.createDrawer();
    }

    createDrawer() {
        const drawerHtml = `
            <div class="journey-drawer" id="journey-drawer">
                <div class="drawer-header">
                    <h5 class="drawer-title">Journey Details</h5>
                    <button class="btn-close" onclick="this.closest('.journey-drawer').classList.remove('open')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="drawer-body">
                    <div id="journey-content"></div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', drawerHtml);
        this.drawer = document.getElementById('journey-drawer');
    }

    show(journeyData) {
        const content = document.getElementById('journey-content');
        
        const timelineHtml = this.generateTimelineHtml(journeyData.timeline);
        
        content.innerHTML = `
            <div class="journey-info mb-4">
                <h6>${journeyData.title}</h6>
                <p class="text-muted">${journeyData.description}</p>
            </div>
            <div class="journey-timeline">
                ${timelineHtml}
            </div>
        `;
        
        this.drawer.classList.add('open');
    }

    generateTimelineHtml(timeline) {
        return timeline.map(item => `
            <div class="timeline-item ${item.status}">
                <div class="timeline-content">
                    <h6>${item.title}</h6>
                    <p class="text-muted">${item.description}</p>
                    <small class="text-muted">${item.timestamp}</small>
                </div>
            </div>
        `).join('');
    }
}

// File Import Modal
class FileImportModal {
    constructor() {
        this.modal = null;
        this.init();
    }

    init() {
        this.createModal();
    }

    createModal() {
        const modalHtml = `
            <div class="modal fade file-import-modal" id="fileImportModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Import Container Data</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="drop-zone" id="dropZone">
                                <div class="icon">
                                    <i class="fas fa-cloud-upload-alt"></i>
                                </div>
                                <div class="text">Drag and drop files here</div>
                                <div class="subtext">or click to browse</div>
                                <input type="file" id="fileInput" multiple accept=".csv,.xlsx,.xls" style="display: none;">
                            </div>
                            <div id="fileList" class="mt-3" style="display: none;">
                                <h6>Selected Files:</h6>
                                <ul id="fileListItems"></ul>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="importBtn" disabled>Import Files</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        this.modal = document.getElementById('fileImportModal');
        this.bindEvents();
    }

    bindEvents() {
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const importBtn = document.getElementById('importBtn');

        // Click to browse
        dropZone.addEventListener('click', () => {
            fileInput.click();
        });

        // Drag and drop events
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            this.handleFiles(files);
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });

        // Import button
        importBtn.addEventListener('click', () => {
            this.importFiles();
        });
    }

    handleFiles(files) {
        const fileList = document.getElementById('fileList');
        const fileListItems = document.getElementById('fileListItems');
        const importBtn = document.getElementById('importBtn');

        if (files.length > 0) {
            fileList.style.display = 'block';
            importBtn.disabled = false;

            fileListItems.innerHTML = '';
            Array.from(files).forEach(file => {
                const li = document.createElement('li');
                li.textContent = `${file.name} (${this.formatFileSize(file.size)})`;
                fileListItems.appendChild(li);
            });
        } else {
            fileList.style.display = 'none';
            importBtn.disabled = true;
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    importFiles() {
        const fileInput = document.getElementById('fileInput');
        const files = fileInput.files;

        if (files.length === 0) return;

        const formData = new FormData();
        Array.from(files).forEach(file => {
            formData.append('files', file);
        });

        // Show loading state
        const importBtn = document.getElementById('importBtn');
        const originalText = importBtn.textContent;
        importBtn.textContent = 'Importing...';
        importBtn.disabled = true;

        // Send to server
        fetch('/api/import-files', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Close modal and show success message
                const modal = bootstrap.Modal.getInstance(this.modal);
                modal.hide();
                
                // Show success flash message
                this.showFlashMessage('Files imported successfully!', 'success');
                
                // Reload page or update data
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                throw new Error(data.message || 'Import failed');
            }
        })
        .catch(error => {
            console.error('Import error:', error);
            this.showFlashMessage('Import failed: ' + error.message, 'error');
        })
        .finally(() => {
            importBtn.textContent = originalText;
            importBtn.disabled = false;
        });
    }

    showFlashMessage(message, type) {
        const flashHtml = `
            <div class="alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = document.querySelector('.container');
        container.insertAdjacentHTML('afterbegin', flashHtml);
    }

    show() {
        const modal = new bootstrap.Modal(this.modal);
        modal.show();
    }
}

// Progress Bar Component
class ProgressBar {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            value: 0,
            max: 100,
            animated: true,
            striped: false,
            ...options
        };
        this.init();
    }

    init() {
        this.render();
    }

    render() {
        const percentage = (this.options.value / this.options.max) * 100;
        const stripedClass = this.options.striped ? 'progress-bar-striped' : '';
        const animatedClass = this.options.animated ? 'progress-bar-animated' : '';
        
        this.container.innerHTML = `
            <div class="progress">
                <div class="progress-bar ${stripedClass} ${animatedClass}" 
                     role="progressbar" 
                     style="width: ${percentage}%" 
                     aria-valuenow="${this.options.value}" 
                     aria-valuemin="0" 
                     aria-valuemax="${this.options.max}">
                    ${this.options.showLabel ? `${percentage.toFixed(1)}%` : ''}
                </div>
            </div>
        `;
    }

    update(value) {
        this.options.value = value;
        this.render();
    }
}

// Badge Component
class Badge {
    constructor(container, text, type = 'secondary') {
        this.container = container;
        this.text = text;
        this.type = type;
        this.init();
    }

    init() {
        this.render();
    }

    render() {
        this.container.innerHTML = `
            <span class="badge bg-${this.type}">${this.text}</span>
        `;
    }
}

// Utility Functions
const Utils = {
    // Format date to local timezone
    formatDate: (date, timezone = 'America/Los_Angeles') => {
        return new Intl.DateTimeFormat('en-US', {
            timeZone: timezone,
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    },

    // Debounce function
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Throttle function
    throttle: (func, limit) => {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // Show notification
    showNotification: (message, type = 'info', duration = 5000) => {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
    }
};

// Initialize components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize file import modal
    window.fileImportModal = new FileImportModal();
    
    // Initialize any existing timelines
    const timelineContainers = document.querySelectorAll('[data-timeline]');
    timelineContainers.forEach(container => {
        const data = JSON.parse(container.dataset.timeline);
        new Timeline(container, data);
    });
    
    // Initialize any existing progress bars
    const progressContainers = document.querySelectorAll('[data-progress]');
    progressContainers.forEach(container => {
        const options = JSON.parse(container.dataset.progress);
        new ProgressBar(container, options);
    });
    
    // Initialize any existing badges
    const badgeContainers = document.querySelectorAll('[data-badge]');
    badgeContainers.forEach(container => {
        const data = JSON.parse(container.dataset.badge);
        new Badge(container, data.text, data.type);
    });
});

// Export classes for global use
window.Timeline = Timeline;
window.JourneyDrawer = JourneyDrawer;
window.FileImportModal = FileImportModal;
window.ProgressBar = ProgressBar;
window.Badge = Badge;
window.Utils = Utils;
