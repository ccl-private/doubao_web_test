from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
import pymysql
from pymysql.cursors import DictCursor

app = Flask(__name__)
CORS(app)

# 配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key'
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST') or 'localhost'
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER') or 'root'
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD') or 'ccl123654789*'
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB') or 'videogenius'


# 数据库连接
def get_db_connection():
    connection = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        charset='utf8mb4',
        cursorclass=DictCursor
    )
    return connection


# 创建数据库表
def init_db():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 创建用户表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(200) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')

            # 检查是否已经有管理员用户
            cursor.execute('SELECT * FROM users WHERE email = %s', ('admin@example.com',))
            admin = cursor.fetchone()

            if not admin:
                # 创建管理员用户
                hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
                cursor.execute('''
                INSERT INTO users (name, email, password) VALUES (%s, %s, %s)
                ''', ('管理员', 'admin@example.com', hashed_password))

        connection.commit()
        print('数据库初始化完成')
    except Exception as e:
        print(f'初始化数据库时出错: {e}')
        connection.rollback()
    finally:
        connection.close()


# 注册接口
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    # 验证请求数据
    if not all(key in data for key in ['name', 'email', 'password']):
        return jsonify({'message': '缺少必要的参数'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 检查邮箱是否已存在
            cursor.execute('SELECT * FROM users WHERE email = %s', (data['email'],))
            if cursor.fetchone():
                return jsonify({'message': '邮箱已被注册'}), 400

            # 哈希密码
            hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

            # 创建新用户
            cursor.execute('''
            INSERT INTO users (name, email, password) VALUES (%s, %s, %s)
            ''', (data['name'], data['email'], hashed_password))

        connection.commit()
        return jsonify({'message': '注册成功'}), 201
    except Exception as e:
        print(f'注册时出错: {e}')
        connection.rollback()
        return jsonify({'message': '注册失败'}), 500
    finally:
        connection.close()


# 登录接口
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    # 验证请求数据
    if not all(key in data for key in ['email', 'password']):
        return jsonify({'message': '缺少必要的参数'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 查找用户
            cursor.execute('SELECT * FROM users WHERE email = %s', (data['email'],))
            user = cursor.fetchone()

            # 检查用户是否存在和密码是否正确
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
    except Exception as e:
        print(f'登录时出错: {e}')
        return jsonify({'message': '登录失败'}), 500
    finally:
        connection.close()


# 验证令牌接口
@app.route('/api/verify-token', methods=['POST'])
def verify_token():
    data = request.get_json()

    # 验证请求数据
    if 'token' not in data:
        return jsonify({'message': '缺少令牌参数'}), 400

    try:
        # 解码令牌
        decoded_data = jwt.decode(data['token'], app.config['SECRET_KEY'], algorithms=['HS256'])

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 查找用户
                cursor.execute('SELECT * FROM users WHERE id = %s', (decoded_data['user_id'],))
                user = cursor.fetchone()

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
        except Exception as e:
            print(f'验证令牌时出错: {e}')
            return jsonify({'message': '验证令牌失败'}), 500
        finally:
            connection.close()
    except jwt.ExpiredSignatureError:
        return jsonify({'message': '令牌已过期'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': '无效的令牌'}), 401
    except Exception as e:
        print(f'验证令牌时出错: {e}')
        return jsonify({'message': '验证令牌失败'}), 500


# 主页路由
@app.route('/')
def index():
    return jsonify({'message': 'VideoGenius API 服务正在运行'}), 200


# 初始化数据库
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
