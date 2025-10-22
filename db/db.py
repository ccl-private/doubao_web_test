import pymysql
from pymysql.cursors import DictCursor
import os
from werkzeug.security import generate_password_hash

# 数据库配置
MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'ccl123654789*'
MYSQL_DB = os.environ.get('MYSQL_DB') or 'videogenius'


def get_db_connection(db_name=MYSQL_DB):
    """获取数据库连接"""
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        db=db_name,
        charset='utf8mb4',
        cursorclass=DictCursor
    )


def init_db():
    """初始化数据库（创建库和表，新增积分字段）"""
    # 先创建数据库（如果不存在）
    connection = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        charset='utf8mb4',
        cursorclass=DictCursor
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{MYSQL_DB}'")
            if not cursor.fetchone():
                cursor.execute(f"CREATE DATABASE {MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"数据库 {MYSQL_DB} 创建成功")
    finally:
        connection.close()

    # 创建表结构（新增积分相关字段）
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 用户表（新增 points 字段存储积分）
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(200) NOT NULL,
                points INT NOT NULL DEFAULT 0,  # 新增：用户积分，默认0
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')

            # 视频任务表（新增 points_consumed 字段记录消耗积分）
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                prompt_id VARCHAR(100) NOT NULL,
                image_path VARCHAR(255) NOT NULL,
                positive_prompt TEXT,
                negative_prompt TEXT,
                width INT,
                height INT,
                length INT,
                fps INT,
                points_consumed INT NOT NULL DEFAULT 0,  # 新增：本次任务消耗的积分
                status VARCHAR(20) DEFAULT 'pending',  # pending/running/completed/failed
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')

            # 创建默认管理员用户（初始化1000积分）
            cursor.execute('SELECT * FROM users WHERE email = %s', ('admin@example.com',))
            if not cursor.fetchone():
                hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
                cursor.execute('''
                INSERT INTO users (name, email, password, points) VALUES (%s, %s, %s, %s)
                ''', ('管理员', 'admin@example.com', hashed_password, 1000))  # 默认1000积分

        connection.commit()
        print("数据库表结构（含积分功能）初始化完成")
    except Exception as e:
        print(f"数据库初始化错误: {str(e)}")
        connection.rollback()
    finally:
        connection.close()


def get_user_by_email(email):
    """通过邮箱查询用户（包含积分）"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            return cursor.fetchone()
    finally:
        connection.close()


def create_user(name, email, hashed_password, initial_points=0):
    """创建新用户（支持初始化积分，默认0）"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('''
            INSERT INTO users (name, email, password, points) VALUES (%s, %s, %s, %s)
            ''', (name, email, hashed_password, initial_points))
        connection.commit()
        return True
    except Exception as e:
        print(f"创建用户错误: {str(e)}")
        connection.rollback()
        return False
    finally:
        connection.close()


def get_user_by_id(user_id):
    """通过ID查询用户（包含积分）"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            return cursor.fetchone()
    finally:
        connection.close()


def update_user_points(user_id, new_points):
    """更新用户积分（直接设置新值）"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('''
            UPDATE users SET points = %s WHERE id = %s
            ''', (new_points, user_id))
        connection.commit()
        return cursor.rowcount > 0  # 成功更新返回True
    except Exception as e:
        print(f"更新用户积分错误: {str(e)}")
        connection.rollback()
        return False
    finally:
        connection.close()


def add_video_task(user_id, prompt_id, image_path, positive_prompt, negative_prompt,
                   width, height, length, fps, points_consumed=0):
    """添加视频任务记录（包含积分消耗）"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('''
            INSERT INTO video_tasks 
            (user_id, prompt_id, image_path, positive_prompt, negative_prompt, 
             width, height, length, fps, points_consumed)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (user_id, prompt_id, image_path, positive_prompt, negative_prompt,
                  width, height, length, fps, points_consumed))
        connection.commit()
        return True
    except Exception as e:
        print(f"添加视频任务错误: {str(e)}")
        connection.rollback()
        return False
    finally:
        connection.close()


def get_user_video_tasks(user_id):
    """查询用户的视频任务（包含积分消耗记录）"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('''
            SELECT id, prompt_id, points_consumed, status, created_at 
            FROM video_tasks 
            WHERE user_id = %s 
            ORDER BY created_at DESC
            ''', (user_id,))
            return cursor.fetchall()
    finally:
        connection.close()