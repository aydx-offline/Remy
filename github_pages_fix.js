// Remy - GitHub Pages 专用修复版
// 解决GitHub Pages上的图片上传问题

console.log('=== Remy GitHub Pages 修复版加载 ===');

(function() {
    console.log('初始化GitHub Pages兼容版本');
    
    // 检测是否在GitHub Pages环境
    const isGitHubPages = window.location.hostname.includes('github.io');
    console.log('GitHub Pages环境:', isGitHubPages);
    
    // 全局变量
    let currentStep = 1;
    let uploadedImage = null;
    
    // 主初始化函数
    function initGitHubPages() {
        console.log('GitHub Pages初始化开始');
        
        try {
            // 等待DOM完全加载
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', setupGitHubPages);
            } else {
                setTimeout(setupGitHubPages, 100);
            }
        } catch (error) {
            console.error('初始化错误:', error);
        }
    }
    
    function setupGitHubPages() {
        console.log('设置GitHub Pages事件监听器');
        
        // 获取所有必需元素
        const elements = {
            uploadArea: document.getElementById('uploadArea'),
            imageInput: document.getElementById('imageInput'),
            useSample1: document.getElementById('useSample1'),
            useSample2: document.getElementById('useSample2'),
            nextStep1: document.getElementById('nextStep1')
        };
        
        console.log('元素检查:', elements);
        
        // 1. 上传区域点击 - 使用最兼容的方式
        if (elements.uploadArea) {
            console.log('设置uploadArea点击事件');
            
            // 移除所有现有事件监听器（避免重复）
            const newUploadArea = elements.uploadArea.cloneNode(true);
            elements.uploadArea.parentNode.replaceChild(newUploadArea, elements.uploadArea);
            
            // 重新获取元素
            const uploadArea = document.getElementById('uploadArea');
            
            // 使用onclick确保最大兼容性
            uploadArea.onclick = function(e) {
                console.log('📱 uploadArea被点击（GitHub Pages）');
                e.stopPropagation();
                
                if (elements.imageInput) {
                    console.log('触发文件选择');
                    elements.imageInput.click();
                } else {
                    console.error('imageInput元素不存在');
                    // 创建临时的文件输入
                    const tempInput = document.createElement('input');
                    tempInput.type = 'file';
                    tempInput.accept = 'image/*';
                    tempInput.style.display = 'none';
                    tempInput.onchange = function(e) {
                        if (e.target.files[0]) {
                            handleImageFile(e.target.files[0]);
                        }
                    };
                    document.body.appendChild(tempInput);
                    tempInput.click();
                    setTimeout(() => document.body.removeChild(tempInput), 100);
                }
            };
            
            // 拖放功能（GitHub Pages可能需要）
            uploadArea.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', function() {
                this.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('dragover');
                
                if (e.dataTransfer.files[0]) {
                    handleImageFile(e.dataTransfer.files[0]);
                }
            });
        }
        
        // 2. 文件输入变化事件
        if (elements.imageInput) {
            elements.imageInput.onchange = function(e) {
                console.log('文件选择变化（GitHub Pages）');
                if (e.target.files[0]) {
                    handleImageFile(e.target.files[0]);
                }
            };
        }
        
        // 3. 示例图片按钮 - 使用绝对URL确保GitHub Pages能访问
        if (elements.useSample1) {
            elements.useSample1.onclick = function() {
                console.log('使用示例图片1（GitHub Pages）');
                useSampleImage('sample1');
            };
        }
        
        if (elements.useSample2) {
            elements.useSample2.onclick = function() {
                console.log('使用示例图片2（GitHub Pages）');
                useSampleImage('sample2');
            };
        }
        
        // 4. 下一步按钮
        if (elements.nextStep1) {
            elements.nextStep1.onclick = function() {
                console.log('下一步按钮（GitHub Pages）');
                goToStep(2);
            };
        }
        
        console.log('GitHub Pages事件监听器设置完成');
        
        // 显示状态信息
        showGitHubPagesStatus();
    }
    
    function handleImageFile(file) {
        console.log('处理图片文件（GitHub Pages）:', file.name, file.type, file.size);
        
        // 基本验证
        if (!file.type.match('image.*')) {
            alert('请选择图片文件（JPG、PNG等）！');
            return;
        }
        
        if (file.size > 5 * 1024 * 1024) {
            alert('图片大小不能超过5MB！');
            return;
        }
        
        // 显示加载状态
        showLoading('正在处理图片...');
        
        // 使用FileReader（GitHub Pages支持）
        const reader = new FileReader();
        
        reader.onloadstart = function() {
            console.log('开始读取文件');
        };
        
        reader.onprogress = function(e) {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                console.log(`读取进度: ${percent}%`);
            }
        };
        
        reader.onload = function(e) {
            console.log('✅ 文件读取成功（GitHub Pages）');
            hideLoading();
            
            uploadedImage = e.target.result;
            showImagePreview(uploadedImage);
            
            // 模拟AI识别
            setTimeout(() => {
                simulateImageRecognition();
            }, 500);
        };
        
        reader.onerror = function(e) {
            console.error('文件读取失败:', e);
            hideLoading();
            alert('读取图片失败，请重试！\n错误: ' + e.target.error.name);
        };
        
        reader.onabort = function() {
            console.log('文件读取被取消');
            hideLoading();
        };
        
        reader.readAsDataURL(file);
    }
    
    function useSampleImage(sampleType) {
        console.log('使用示例图片:', sampleType);
        
        // 使用可靠的图片URL（确保GitHub Pages能访问）
        let imageUrl = '';
        
        if (sampleType === 'sample1') {
            // 使用可靠的图床
            imageUrl = 'https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=800&auto=format&fit=crop&q=80';
        } else {
            imageUrl = 'https://images.unsplash.com/photo-1571171637578-41bc2dd41cd2?w=800&auto=format&fit=crop&q=80';
        }
        
        // 显示加载状态
        showLoading('正在加载示例图片...');
        
        // 预加载图片确保可用
        const img = new Image();
        img.onload = function() {
            console.log('✅ 示例图片加载成功');
            hideLoading();
            
            uploadedImage = imageUrl;
            showImagePreview(uploadedImage);
            
            // 模拟AI识别
            setTimeout(() => {
                simulateImageRecognition();
            }, 500);
        };
        
        img.onerror = function() {
            console.error('示例图片加载失败');
            hideLoading();
            alert('示例图片加载失败，请检查网络连接或使用自己的图片。');
            
            // 使用备用图片
            uploadedImage = 'data:image/svg+xml;base64,' + btoa(
                '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">' +
                '<rect width="100%" height="100%" fill="#4CAF50"/>' +
                '<text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="white" font-size="20">' +
                '示例图片（网络加载失败）</text></svg>'
            );
            showImagePreview(uploadedImage);
        };
        
        img.src = imageUrl;
    }
    
    function showImagePreview(imageData) {
        console.log('显示图片预览');
        const uploadArea = document.getElementById('uploadArea');
        if (!uploadArea) return;
        
        uploadArea.innerHTML = `
            <div class="text-center">
                <img src="${imageData}" alt="预览" class="img-fluid rounded" style="max-height: 300px; max-width: 100%;">
                <p class="mt-3 text-success">
                    <i class="fas fa-check-circle me-1"></i>图片已上传（GitHub Pages）
                </p>
                <button class="btn btn-outline-secondary btn-sm" id="reuploadBtn">
                    <i class="fas fa-redo me-1"></i>重新上传
                </button>
            </div>
        `;
        
        // 启用下一步按钮
        const nextStep1 = document.getElementById('nextStep1');
        if (nextStep1) {
            nextStep1.disabled = false;
            console.log('下一步按钮已启用');
        }
        
        // 重新上传按钮
        document.getElementById('reuploadBtn').onclick = function() {
            console.log('重新上传按钮点击');
            resetUploadArea();
        };
    }
    
    function resetUploadArea() {
        console.log('重置上传区域');
        const uploadArea = document.getElementById('uploadArea');
        
        // 使用原始HTML结构
        uploadArea.innerHTML = `
            <i class="fas fa-cloud-upload-alt fa-3x mb-3" style="color: #4CAF50;"></i>
            <h4>拖放图片或点击上传</h4>
            <p class="text-muted">支持 JPG、PNG 格式，最大 5MB</p>
            <input type="file" id="imageInput" accept="image/*" class="d-none">
            <p class="mt-3">
                <small class="text-muted">或使用示例图片：</small>
                <button class="btn btn-outline-primary btn-sm ms-2" id="useSample1">
                    <i class="fas fa-image me-1"></i>示例1
                </button>
                <button class="btn btn-outline-primary btn-sm ms-2" id="useSample2">
                    <i class="fas fa-image me-1"></i>示例2
                </button>
            </p>
        `;
        
        // 重新初始化
        setTimeout(() => {
            setupGitHubPages();
        }, 100);
    }
    
    function simulateImageRecognition() {
        console.log('模拟图片识别（GitHub Pages）...');
        showLoading('正在识别食材...');
        
        setTimeout(() => {
            hideLoading();
            console.log('识别完成');
            
            // 这里可以添加识别结果的显示逻辑
            alert('✅ 图片识别完成！\n检测到：鸡蛋、西红柿、牛奶等食材。\n（GitHub Pages演示版）');
        }, 1500);
    }
    
    function goToStep(step) {
        console.log('跳转到步骤:', step);
        // 简化的步骤切换逻辑
        // 可以根据需要实现完整的步骤切换
    }
    
    function showLoading(message) {
        console.log('显示加载:', message);
        // 可以添加加载动画
    }
    
    function hideLoading() {
        console.log('隐藏加载');
        // 可以移除加载动画
    }
    
    function showGitHubPagesStatus() {
        // 在页面底部显示状态信息
        const statusDiv = document.createElement('div');
        statusDiv.id = 'githubPagesStatus';
        statusDiv.style.cssText = `
            position: fixed;
            bottom: 10px;
            right: 10px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 8px 12px;
            border-radius: 5px;
            font-size: 12px;
            z-index: 9999;
        `;
        statusDiv.innerHTML = `
            <div>GitHub Pages模式</div>
            <div>上传功能: <span style="color: #4CAF50;">已启用</span></div>
        `;
        document.body.appendChild(statusDiv);
    }
    
    // 启动初始化
    initGitHubPages();
    
    // 全局调试函数
    window.debugGitHubPages = function() {
        console.log('=== GitHub Pages调试信息 ===');
        console.log('URL:', window.location.href);
        console.log('User Agent:', navigator.userAgent);
        console.log('FileReader支持:', !!window.FileReader);
        console.log('File API支持:', !!window.File);
        console.log('FormData支持:', !!window.FormData);
        console.log('=== 调试结束 ===');
    };
    
})();

console.log('=== Remy GitHub Pages 修复版加载完成 ===');