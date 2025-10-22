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
    // 新增：获取宽度、高度、fps的DOM元素（假设你的HTML中有这些控件）
    const videoWidth = document.getElementById('video-width');
    const videoHeight = document.getElementById('video-height');
    const videoFps = document.getElementById('video-fps');

    if (generateButton) {
        generateButton.addEventListener('click', async function() {
            if (!videoPrompt.value.trim()) {
                alert('请输入视频描述');
                return;
            }

            // 检查用户是否已登录
            const token = localStorage.getItem('token');
            if (!token) {
                openLoginModal();
                return;
            }

            // 显示生成状态
            generationStatus.classList.remove('hidden');
            generationResult.classList.add('hidden');

            try {
                // 构建参数对象（包含所有必要参数）
                const params = {
                    prompt: videoPrompt.value,
                    style: videoStyle.value,
                    duration: videoDuration.value,
                    width: videoWidth.value,
                    height: videoHeight.value,
                    fps: videoFps.value
                };

                // 调用后端API生成视频（传递token和params）
                const result = await generateVideoByText(token, params);

                // 隐藏状态，显示结果
                generationStatus.classList.add('hidden');
                generationResult.classList.remove('hidden');
                alert(`视频生成任务已提交，任务ID：${result.promptId}，消耗积分：${result.pointsConsumed}`);
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
                // 1. 收集参数（构建params对象，而非直接构建formData）
                const params = {
                    positivePrompt: document.getElementById('positive-prompt').value,
                    negativePrompt: document.getElementById('negative-prompt').value,
                    width: document.getElementById('video-width').value,
                    height: document.getElementById('video-height').value,
                    fps: document.getElementById('video-fps').value,
                    length: document.getElementById('video-length').value
                };

                // 2. 获取图片文件
                const imageFile = imageUpload.files[0];

                // 3. 调用API生成视频（按api.js要求传递参数：token, imageFile, params）
                const result = await generateVideoByImage(token, imageFile, params);

                // 4. 显示结果（注意：后端返回的是任务ID，不是直接的videoUrl）
                generationStatus.classList.add('hidden');
                generationResult.classList.remove('hidden');
                alert(`视频生成任务已提交，任务ID：${result.promptId}，消耗积分：${result.pointsConsumed}`);
                // 若后续需要展示视频，需根据promptId轮询后端结果
            } catch (error) {
                generationStatus.classList.add('hidden');
                alert(`生成视频失败: ${error.message}`);
            }
        });
    }
}