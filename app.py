from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from functools import wraps

# 导入自定义模块
from db import db # 数据库模块
import utils  # 工具函数
from ai.comfyui_functions import load_prompt_template, submit_comfyui_task  # AI功能模块

# 初始化Flask应用
app = Flask(__name__)
CORS(app)

# 配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key'
COMFYUI_URL = "http://192.168.2.158:8188/prompt"  # ComfyUI地址
PROMPT_TEMPLATE_PATH = "video_wan2_2_14B_i2v.json"  # 提示词模板路径


# JWT认证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # 从请求头获取token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None

        if not token:
            return jsonify({'message': '令牌缺失'}), 401

        try:
            # 解码令牌
            decoded_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = db.get_user_by_id(decoded_data['user_id'])
            if not current_user:
                return jsonify({'message': '用户不存在'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': '令牌已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': '无效的令牌'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# 注册接口
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    # 验证请求数据
    if not all(key in data for key in ['name', 'email', 'password']):
        return jsonify({'message': '缺少必要的参数'}), 400

    # 检查邮箱是否已存在
    if db.get_user_by_email(data['email']):
        return jsonify({'message': '邮箱已被注册'}), 400

    # 哈希密码并创建用户
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    if db.create_user(data['name'], data['email'], hashed_password):
        return jsonify({'message': '注册成功'}), 201
    else:
        return jsonify({'message': '注册失败'}), 500


# 登录接口
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    # 验证请求数据
    if not all(key in data for key in ['email', 'password']):
        return jsonify({'message': '缺少必要的参数'}), 400

    # 查找用户
    user = db.get_user_by_email(data['email'])
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'message': '邮箱或密码错误'}), 401

    # 生成JWT令牌
    token = jwt.encode({
        'user_id': user['id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({
        'message': '登录成功',
        'token': token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email']
        }
    }), 200


# 验证令牌接口
@app.route('/api/verify-token', methods=['POST'])
def verify_token():
    data = request.get_json()
    if 'token' not in data:
        return jsonify({'message': '缺少令牌参数'}), 400

    try:
        decoded_data = jwt.decode(data['token'], app.config['SECRET_KEY'], algorithms=['HS256'])
        user = db.get_user_by_id(decoded_data['user_id'])
        if not user:
            return jsonify({'message': '用户不存在'}), 404

        return jsonify({
            'message': '令牌有效',
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email']
            }
        }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'message': '令牌已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': '无效的令牌'}), 401
    except Exception as e:
        print(f'验证令牌错误: {e}')
        return jsonify({'message': '验证令牌失败'}), 500


# 视频生成接口（需要认证）
@app.route('/api/generate-video', methods=['POST'])
@token_required
def generate_video(current_user):
    """生成视频接口（需要登录）"""
    data = request.get_json()
    if not data:
        return jsonify({'message': '请求格式错误，请使用JSON'}), 400

    # 验证必填参数
    required_fields = [
        'image_base64', 'positive_prompt', 'negative_prompt',
        'width', 'height', 'length', 'fps'
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'缺少必要的参数: {field}'}), 400

    try:
        # 1. 保存图片（使用用户邮箱生成文件名）
        save_success, image_path, save_error = utils.save_base64_image(
            base64_str=data['image_base64'],
            email=current_user['email']
        )
        if not save_success:
            return jsonify({'message': save_error}), 400

        # 2. 加载提示词模板
        try:
            prompt_template = load_prompt_template(PROMPT_TEMPLATE_PATH)
        except Exception as e:
            return jsonify({'message': f'加载模板失败: {str(e)}'}), 500

        # 3. 生成文件名前缀
        safe_email = current_user['email'].replace('@', '_').replace('.', '_')
        filename_prefix = f"video/{safe_email}_{int(datetime.datetime.now().timestamp())}"

        # 4. 提交任务到ComfyUI
        success, prompt_id, error = submit_comfyui_task(
            prompt_template=prompt_template,
            comfyui_url=COMFYUI_URL,
            image_path=image_path,
            positive_prompt=data['positive_prompt'],
            negative_prompt=data['negative_prompt'],
            width=int(data['width']),
            height=int(data['height']),
            length=int(data['length']),
            fps=int(data['fps']),
            filename_prefix=filename_prefix
        )

        if not success:
            return jsonify({'message': f'任务提交失败: {error}'}), 500

        # 5. 记录任务到数据库
        db.add_video_task(
            user_id=current_user['id'],
            prompt_id=prompt_id,
            image_path=image_path,
            positive_prompt=data['positive_prompt'],
            negative_prompt=data['negative_prompt'],
            width=int(data['width']),
            height=int(data['height']),
            length=int(data['length']),
            fps=int(data['fps'])
        )

        return jsonify({
            'message': '视频生成任务已提交',
            'prompt_id': prompt_id
        }), 200

    except Exception as e:
        print(f'视频生成接口错误: {str(e)}')
        return jsonify({'message': '服务器内部错误'}), 500


# 首页路由
@app.route('/')
def index():
    return render_template('index.html')


# 初始化数据库
with app.app_context():
    db.init_db()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)