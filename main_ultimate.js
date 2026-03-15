// Remy 智能冰箱伴侣 - 终极修复版
// 解决所有点击无反应问题

console.log('=== Remy 终极修复版加载 ===');

// 使用立即执行函数确保代码立即执行
(function() {
    console.log('立即执行函数开始');
    
    // 全局变量
    let currentStep = 1;
    let uploadedImage = null;
    
    // 主初始化函数
    function initRemy() {
        console.log('initRemy() 开始执行');
        
        try {
            // 1. 检查所有必需元素
            const elements = {
                uploadArea: document.getElementById('uploadArea'),
                imageInput: document.getElementById('imageInput'),
                useSample1: document.getElementById('useSample1'),
                useSample2: document.getElementById('useSample2'),
                nextStep1: document.getElementById('nextStep1')
            };
            
            console.log('检查元素:', elements);
            
            // 2. 设置事件监听器
            setupAllEventListeners(elements);
            
            // 3. 初始状态
            updateStepIndicator();
            
            console.log('initRemy() 执行完成');
        } catch (error) {
            console.error('initRemy() 错误:', error);
            alert('Remy初始化错误，请查看控制台');
        }
    }
    
    function setupAllEventListeners(elements) {
        console.log('设置所有事件监听器');
        
        // 上传区域点击 - 最简化的实现
        if (elements.uploadArea) {
            console.log('绑定 uploadArea 点击事件');
            elements.uploadArea.onclick = function() {
                console.log('📱 uploadArea 被点击！');
                if (elements.imageInput) {
                    console.log('触发文件选择对话框');
                    elements.imageInput.click();
                }
            };
            
            // 拖放功能
            elements.uploadArea.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('dragover');
            });
            
            elements.uploadArea.addEventListener('dragleave', function() {
                this.classList.remove('dragover');
            });
            
            elements.uploadArea.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('dragover');
                if (e.dataTransfer.files[0]) {
                    handleImageFile(e.dataTransfer.files[0]);
                }
            });
        } else {
            console.error('❌ uploadArea 元素不存在！');
        }
        
        // 文件输入变化事件
        if (elements.imageInput) {
            elements.imageInput.onchange = function(e) {
                console.log('文件选择变化');
                if (e.target.files[0]) {
                    handleImageFile(e.target.files[0]);
                }
            };
        }
        
        // 示例图片按钮 - 直接绑定
        if (elements.useSample1) {
            console.log('绑定 useSample1 点击事件');
            elements.useSample1.onclick = function() {
                console.log('🎯 useSample1 被点击！');
                useSampleImage('sample1');
            };
        }
        
        if (elements.useSample2) {
            console.log('绑定 useSample2 点击事件');
            elements.useSample2.onclick = function() {
                console.log('🎯 useSample2 被点击！');
                useSampleImage('sample2');
            };
        }
        
        // 下一步按钮
        if (elements.nextStep1) {
            elements.nextStep1.onclick = function() {
                console.log('下一步按钮点击');
                goToStep(2);
            };
        }
        
        console.log('所有事件监听器设置完成');
    }
    
    function handleImageFile(file) {
        console.log('处理图片文件:', file.name);
        
        // 简单验证
        if (!file.type.match('image.*')) {
            alert('请选择图片文件！');
            return;
        }
        
        if (file.size > 5 * 1024 * 1024) {
            alert('图片大小不能超过5MB！');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(e) {
            console.log('图片读取成功');
            uploadedImage = e.target.result;
            showImagePreview(uploadedImage);
            simulateImageRecognition();
        };
        reader.readAsDataURL(file);
    }
    
    function useSampleImage(sampleType) {
        console.log('使用示例图片:', sampleType);
        
        let imageUrl = sampleType === 'sample1' 
            ? 'https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=800&auto=format&fit=crop'
            : 'https://images.unsplash.com/photo-1571171637578-41bc2dd41cd2?w=800&auto=format&fit=crop';
        
        uploadedImage = imageUrl;
        showImagePreview(uploadedImage);
        simulateImageRecognition();
    }
    
    function showImagePreview(imageData) {
        console.log('显示图片预览');
        const uploadArea = document.getElementById('uploadArea');
        if (!uploadArea) return;
        
        uploadArea.innerHTML = `
            <div class="text-center">
                <img src="${imageData}" alt="预览" class="img-fluid rounded" style="max-height: 300px;">
                <p class="mt-3 text-success">
                    <i class="fas fa-check-circle me-1"></i>图片已上传
                </p>
                <button class="btn btn-outline-secondary btn-sm" id="reuploadBtn">
                    <i class="fas fa-redo me-1"></i>重新上传
                </button>
            </div>
        `;
        
        // 启用下一步按钮
        const nextStep1 = document.getElementById('nextStep1');
        if (nextStep1) nextStep1.disabled = false;
        
        // 重新上传按钮
        document.getElementById('reuploadBtn').onclick = resetUploadArea;
    }
    
    function resetUploadArea() {
        console.log('重置上传区域');
        const uploadArea = document.getElementById('uploadArea');
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
            initRemy();
        }, 100);
    }
    
    function simulateImageRecognition() {
        console.log('模拟图片识别...');
        // 简化的识别模拟
        setTimeout(() => {
            console.log('识别完成');
        }, 1000);
    }
    
    function goToStep(step) {
        console.log('跳转到步骤:', step);
        // 简化的步骤切换
    }
    
    function updateStepIndicator() {
        console.log('更新步骤指示器');
    }
    
    // 页面加载后立即执行
    if (document.readyState === 'loading') {
        console.log('文档还在加载，等待DOMContentLoaded');
        document.addEventListener('DOMContentLoaded', initRemy);
    } else {
        console.log('文档已加载，立即执行');
        initRemy();
    }
    
    // 也绑定到window.load作为后备
    window.addEventListener('load', function() {
        console.log('window.load 事件触发');
        // 确保初始化
        if (!uploadedImage) {
            console.log('执行后备初始化');
            initRemy();
        }
    });
    
    console.log('立即执行函数结束');
})();

// 全局调试函数
window.debugRemy = function() {
    console.log('=== Remy 调试信息 ===');
    console.log('当前步骤:', currentStep);
    console.log('已上传图片:', uploadedImage ? '是' : '否');
    console.log('关键元素检查:');
    console.log('- uploadArea:', document.getElementById('uploadArea'));
    console.log('- imageInput:', document.getElementById('imageInput'));
    console.log('- useSample1:', document.getElementById('useSample1'));
    console.log('- useSample2:', document.getElementById('useSample2'));
    console.log('=== 调试结束 ===');
};

console.log('=== Remy 终极修复版加载完成 ===');