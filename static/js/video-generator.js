import { generateVideoByText, generateVideoByImage } from './api.js';
import { openLoginModal } from './modals.js';

// 文本生成视频逻辑
export function initTextVideoGenerator() {
    const generateButton = document.getElementById('generate-button');
    const generationStatus = document.getElementById('generation-status');
    const generationResult = document.getElementById('generation-result');
    const videoPrompt = document.getElementById('video-prompt');
    const videoStyle = document.getElementById('video-style');
    const videoDuration = document.getElementById('video-duration');

    if (generateButton) {
        generateButton.addEventListener('click', async function() {
            if (!videoPrompt.value.trim()) {
                alert('请输入视频描述');
                return;
            }

            // 检查用户是否已登录
            const token = localStorage.getItem('token');
            if (!token) {
                // 用户未登录，打开登录模态框
                openLoginModal();
                return;
            }

            // 显示生成状态
            generationStatus.classList.remove('hidden');
            generationResult.classList.add('hidden');

            try {
                // 调用后端API生成视频
                const videoUrl = await generateVideoByText(
                    token,
                    videoPrompt.value,
                    videoStyle.value,
                    videoDuration.value
                );

                // 隐藏状态，显示结果
                generationStatus.classList.add('hidden');
                generationResult.classList.remove('hidden');

                // 设置生成的视频源
                document.getElementById('generated-video').src = videoUrl;
            } catch (error) {
                generationStatus.classList.add('hidden');
                alert(`生成视频失败: ${error.message}`);
            }
        });
    }
}

// 图片生成视频逻辑（包含上传预览、拖放等）
export function initImageVideoGenerator() {
    const imageUploadArea = document.getElementById('image-upload-area');
    const imageUpload = document.getElementById('image-upload');
    const imagePreview = document.getElementById('uploaded-image-preview');
    const generationStatus = document.getElementById('generation-status');
    const generationResult = document.getElementById('generation-result');

    // 图片上传区域点击触发文件选择
    if (imageUploadArea && imageUpload) {
        imageUploadArea.addEventListener('click', function() {
            imageUpload.click();
        });
    }

    // 图片预览功能
    if (imageUpload && imagePreview) {
        imageUpload.addEventListener('change', function(e) {
            if (e.target.files && e.target.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.innerHTML = `<img src="${e.target.result}" alt="预览图" class="w-full h-auto rounded-lg">`;
                    imagePreview.classList.remove('hidden');
                }
                reader.readAsDataURL(e.target.files[0]);
            }
        });
    }

    // 拖放功能
    if (imageUploadArea) {
        imageUploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            imageUploadArea.classList.add('border-primary');
        });

        imageUploadArea.addEventListener('dragleave', function() {
            imageUploadArea.classList.remove('border-primary');
        });

        imageUploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            imageUploadArea.classList.remove('border-primary');

            if (e.dataTransfer.files && e.dataTransfer.files[0] && imageUpload) {
                // 将拖放的文件赋值给file input
                imageUpload.files = e.dataTransfer.files;

                // 预览图片
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.innerHTML = `<img src="${e.target.result}" alt="预览图" class="w-full h-auto rounded-lg">`;
                    imagePreview.classList.remove('hidden');
                }
                reader.readAsDataURL(e.dataTransfer.files[0]);
            }
        });
    }

    // 生成按钮点击事件（图片生视频）
    const imageGenerateButton = document.getElementById('image-generate-button');
    if (imageGenerateButton) {
        imageGenerateButton.addEventListener('click', async function() {
            // 简单验证
            if (!imageUpload.files || imageUpload.files.length === 0) {
                alert('请先上传图片');
                return;
            }

            // 检查登录状态
            const token = localStorage.getItem('token');
            if (!token) {
                openLoginModal();
                return;
            }

            // 显示生成状态
            generationStatus.classList.remove('hidden');
            generationResult.classList.add('hidden');

            try {
                // 收集参数
                const formData = new FormData();
                formData.append('image', imageUpload.files[0]);
                formData.append('positive_prompt', document.getElementById('positive-prompt').value);
                formData.append('negative_prompt', document.getElementById('negative-prompt').value);
                formData.append('width', document.getElementById('video-width').value);
                formData.append('height', document.getElementById('video-height').value);
                formData.append('fps', document.getElementById('video-fps').value);
                formData.append('length', document.getElementById('video-length').value);
                formData.append('token', token);

                // 调用API生成视频
                const videoUrl = await generateVideoByImage(formData);

                // 显示结果
                generationStatus.classList.add('hidden');
                generationResult.classList.remove('hidden');
                document.getElementById('generated-video').src = videoUrl;
                document.getElementById('generated-video').load();
            } catch (error) {
                generationStatus.classList.add('hidden');
                alert(`生成视频失败: ${error.message}`);
            }
        });
    }
}