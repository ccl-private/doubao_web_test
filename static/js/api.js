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

        // 保存token和用户信息（含积分，用于前端展示）
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));

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

        // 更新本地用户信息（含积分）
        localStorage.setItem('user', JSON.stringify(data.user));
        return data;
    } catch (error) {
        console.error('验证令牌错误:', error);
        throw error;
    }
}

// API调用函数 - 生成视频（图片）
export async function generateVideoByImage(token, imageFile, params) {
    try {
        const formData = new FormData();
        // 图片文件（二进制）
        formData.append('image', imageFile);
        // 其他参数（按后端要求传递）
        formData.append('positive_prompt', params.positivePrompt);
        formData.append('negative_prompt', params.negativePrompt);
        formData.append('width', params.width);
        formData.append('height', params.height);
        formData.append('length', params.length); // 视频长度
        formData.append('fps', params.fps);

        const response = await fetch(`${API_BASE_URL}/generate-video`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}` // Token通过请求头传递
            },
            body: formData // 无需设置Content-Type，浏览器自动处理
        });

        const data = await response.json();

        // 后端已处理积分校验，前端直接接收结果
        if (!response.ok) {
            // 若积分不足，后端会返回402状态码和具体信息
            throw new Error(data.message || '生成视频失败');
        }

        // 返回任务ID和积分变动信息（供前端展示）
        return {
            promptId: data.prompt_id,
            pointsConsumed: data.points_consumed,
            remainingPoints: data.remaining_points
        };
    } catch (error) {
        console.error('图片生成视频错误:', error);
        throw error; // 抛出错误，由前端页面提示用户（如积分不足）
    }
}

// API调用函数 - 生成视频（文本）
export async function generateVideoByText(token, params) {
    try {
        const formData = new FormData();
        // 文本生成参数
        formData.append('prompt', params.prompt);
        formData.append('style', params.style);
        formData.append('length', params.duration); // 对应视频长度
        formData.append('width', params.width);
        formData.append('height', params.height);
        formData.append('fps', params.fps);

        const response = await fetch(`${API_BASE_URL}/generate-video`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || '文本生成视频失败');
        }

        return {
            promptId: data.prompt_id,
            pointsConsumed: data.points_consumed,
            remainingPoints: data.remaining_points
        };
    } catch (error) {
        console.error('文本生成视频错误:', error);
        throw error;
    }
}

// 获取用户当前积分（仅用于前端展示，不参与校验）
export async function getUserPoints(token) {
    try {
        const response = await fetch(`${API_BASE_URL}/user/points`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || '获取积分失败');
        }

        return data.points;
    } catch (error) {
        console.error('获取积分错误:', error);
        throw error;
    }
}