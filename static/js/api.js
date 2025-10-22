// API基础URL（使用相对路径）
export const API_BASE_URL = '/api';

// API调用函数 - 注册用户
export async function registerUser(name, email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                email: email,
                password: password
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || '注册失败');
        }

        return data;
    } catch (error) {
        console.error('注册错误:', error);
        throw error;
    }
}

// API调用函数 - 用户登录
export async function loginUser(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || '登录失败');
        }

        return data;
    } catch (error) {
        console.error('登录错误:', error);
        throw error;
    }
}

// API调用函数 - 验证令牌
export async function verifyToken(token) {
    try {
        const response = await fetch(`${API_BASE_URL}/verify-token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                token: token
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || '令牌无效');
        }

        return data;
    } catch (error) {
        console.error('验证令牌错误:', error);
        throw error;
    }
}

// API调用函数 - 生成视频（文本）
export async function generateVideoByText(token, prompt, style, duration) {
    try {
        const response = await fetch(`${API_BASE_URL}/generate-video`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                token: token,
                prompt: prompt,
                style: style,
                duration: duration
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || '生成视频失败');
        }

        return data.video_url;
    } catch (error) {
        console.error('生成视频错误:', error);
        throw error;
    }
}

// API调用函数 - 生成视频（图片）
export async function generateVideoByImage(formData) {
    try {
        const response = await fetch(`${API_BASE_URL}/generate-video-from-image`, {
            method: 'POST',
            body: formData, // 注意：FormData无需设置Content-Type
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || '图片生成视频失败');
        }

        return data.video_url;
    } catch (error) {
        console.error('图片生成视频错误:', error);
        throw error;
    }
}