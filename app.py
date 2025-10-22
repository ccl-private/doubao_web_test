from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename  # 用于安全处理文件名
import jwt
import datetime
import os
import uuid  # 用于生成唯一文件名
from functools import wraps

# 导入自定义模块
from db import db  # 数据库模块（已包含积分相关函数）
import utils  # 工具函数（可移除Base64相关代码）
from ai.comfyui_functions import load_prompt_template, submit_comfyui_task  # AI功能模块

# 初始化Flask应用
app = Flask(__name__)
CORS(app)

# 配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/upload'  # 图片上传目录
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 限制上传文件大小（10MB）
COMFYUI_URL = "http://192.168.2.158:8188/prompt"  # ComfyUI地址
PROMPT_TEMPLATE_PATH = "ai/video_wan2_2_14B_i2v.json"  # 提示词模板路径

# 创建上传目录（如果不存在）
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 如果localtest = True，说明本后端服务和COMFYUI服务不在同一台服务器，也没有共享目录，目录是nfs的，两台机器同一文件夹目录不太一致
localtest = True
if localtest:
    app.config['UPLOAD_FOLDER'] = '/mnt/mnt158_hdd/ccl/temp_images'  # 图片上传目录



# JWT认证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None

        if not token:
            return jsonify({'message': '令牌缺失'}), 401

        try:
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
    if not all(key in data for key in ['name', 'email', 'password']):
        return jsonify({'message': '缺少必要的参数'}), 400

    if db.get_user_by_email(data['email']):
        return jsonify({'message': '邮箱已被注册'}), 400

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    if db.create_user(
            name=data['name'],
            email=data['email'],
            hashed_password=hashed_password,
            initial_points=data.get('initial_points', 0)
    ):
        return jsonify({'message': '注册成功'}), 201
    else:
        return jsonify({'message': '注册失败'}), 500


# 登录接口
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not all(key in data for key in ['email', 'password']):
        return jsonify({'message': '缺少必要的参数'}), 400

    user = db.get_user_by_email(data['email'])
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'message': '邮箱或密码错误'}), 401

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
            'email': user['email'],
            'points': user['points']
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
                'email': user['email'],
                'points': user['points']
            }
        }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'message': '令牌已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': '无效的令牌'}), 401
    except Exception as e:
        print(f'验证令牌错误: {e}')
        return jsonify({'message': '验证令牌失败'}), 500


# 视频生成接口（二进制文件上传版）
@app.route('/api/generate-video', methods=['POST'])
@token_required
def generate_video(current_user):
    """生成视频接口（使用FormData上传图片，二进制处理）"""
    # 1. 验证请求格式（FormData）
    if 'image' not in request.files:
        return jsonify({'message': '缺少图片文件'}), 400

    # 2. 获取图片文件和其他参数
    image_file = request.files['image']
    positive_prompt = request.form.get('positive_prompt', '')
    negative_prompt = request.form.get('negative_prompt', '')

    # 验证必要参数
    required_form_fields = ['width', 'height', 'length', 'fps']
    for field in required_form_fields:
        if field not in request.form:
            return jsonify({'message': f'缺少必要的参数: {field}'}), 400

    try:
        # 转换参数为整数
        width = int(request.form['width'])
        height = int(request.form['height'])
        length = int(request.form['length'])
        fps = int(request.form['fps'])
    except ValueError:
        return jsonify({'message': '参数格式错误，宽度/高度/长度/FPS必须为整数'}), 400

    try:
        # 3. 积分校验
        user_points = current_user['points']
        video_resolution = width * height
        required_points = 50

        if user_points < required_points:
            return jsonify({
                'message': '积分不足，无法生成视频',
                'current_points': user_points,
                'required_points': required_points
            }), 402

        # 4. 保存图片（二进制直接保存，无需Base64解码）
        # 生成唯一文件名（避免重复）
        filename = f"{current_user['id']}_{uuid.uuid4()}_{secure_filename(image_file.filename)}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # 保存二进制文件
        try:
            image_file.save(image_path)
        except Exception as e:
            return jsonify({'message': f'图片保存失败: {str(e)}'}), 500

        # 5. 加载提示词模板
        try:
            prompt_template = load_prompt_template(PROMPT_TEMPLATE_PATH)
        except Exception as e:
            return jsonify({'message': f'加载模板失败: {str(e)}'}), 500

        # 6. 生成文件名前缀
        safe_email = current_user['email'].replace('@', '_').replace('.', '_')
        filename_prefix = f"video/{safe_email}_{int(datetime.datetime.now().timestamp())}"

        if localtest:
            image_path_ = image_path.replace('/mnt/mnt158_hdd/', '/slow_disk/')
        else:
            image_path_ = image_path

        # 7. 提交任务到ComfyUI
        success, prompt_id, error = submit_comfyui_task(
            prompt_template=prompt_template,
            comfyui_url=COMFYUI_URL,
            image_path=image_path_,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            length=length,
            fps=fps,
            filename_prefix=filename_prefix
        )

        if not success:
            # 任务失败时删除已保存的图片
            if os.path.exists(image_path):
                os.remove(image_path)
            return jsonify({'message': f'任务提交失败: {error}'}), 500

        # 8. 扣减用户积分
        remaining_points = user_points - required_points
        if not db.update_user_points(current_user['id'], remaining_points):
            # 积分扣减失败，回滚任务和图片
            if os.path.exists(image_path):
                os.remove(image_path)
            print(f"警告：用户 {current_user['id']} 积分扣减失败")
            return jsonify({'message': '积分扣减失败，请重试'}), 500

        # 9. 记录任务（包含积分消耗）
        if not db.add_video_task(
                user_id=current_user['id'],
                prompt_id=prompt_id,
                image_path=image_path,
                positive_prompt=positive_prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                length=length,
                fps=fps,
                points_consumed=required_points
        ):
            print(f"警告：用户 {current_user['id']} 任务记录失败")

        # 10. 返回结果
        return jsonify({
            'message': '视频生成任务已提交',
            'prompt_id': prompt_id,
            'points_consumed': required_points,
            'remaining_points': remaining_points
        }), 200

    except Exception as e:
        print(f'视频生成接口错误: {str(e)}')
        return jsonify({'message': '服务器内部错误'}), 500


# 新增接口：查询用户积分
@app.route('/api/user/points', methods=['GET'])
@token_required
def get_user_points(current_user):
    return jsonify({
        'user_id': current_user['id'],
        'points': current_user['points']
    }), 200


# 新增接口：查询用户任务历史
@app.route('/api/user/tasks', methods=['GET'])
@token_required
def get_user_tasks(current_user):
    tasks = db.get_user_video_tasks(current_user['id'])
    return jsonify({'tasks': tasks}), 200


# 首页路由
@app.route('/')
def index():
    return render_template('index.html')


# 初始化数据库
with app.app_context():
    db.init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)