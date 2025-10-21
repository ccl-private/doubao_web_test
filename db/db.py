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
    """初始化数据库（创建库和表）"""
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

    # 创建表结构
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 用户表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(200) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')

            # 视频任务表（新增，用于记录生成的视频任务）
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
                status VARCHAR(20) DEFAULT 'pending',  # pending/running/completed/failed
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')

            # 创建默认管理员用户（如果不存在）
            cursor.execute('SELECT * FROM users WHERE email = %s', ('admin@example.com',))
            if not cursor.fetchone():
                hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
                cursor.execute('''
                INSERT INTO users (name, email, password) VALUES (%s, %s, %s)
                ''', ('管理员', 'admin@example.com', hashed_password))

        connection.commit()
        print("数据库表结构初始化完成")
    except Exception as e:
        print(f"数据库初始化错误: {str(e)}")
        connection.rollback()
    finally:
        connection.close()


def get_user_by_email(email):
    """通过邮箱查询用户"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            return cursor.fetchone()
    finally:
        connection.close()


def create_user(name, email, hashed_password):
    """创建新用户"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('''
            INSERT INTO users (name, email, password) VALUES (%s, %s, %s)
            ''', (name, email, hashed_password))
        connection.commit()
        return True
    except Exception as e:
        print(f"创建用户错误: {str(e)}")
        connection.rollback()
        return False
    finally:
        connection.close()


def get_user_by_id(user_id):
    """通过ID查询用户"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            return cursor.fetchone()
    finally:
        connection.close()


def add_video_task(user_id, prompt_id, image_path, positive_prompt, negative_prompt, width, height, length, fps):
    """添加视频任务记录"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute('''
            INSERT INTO video_tasks 
            (user_id, prompt_id, image_path, positive_prompt, negative_prompt, width, height, length, fps)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (user_id, prompt_id, image_path, positive_prompt, negative_prompt, width, height, length, fps))
        connection.commit()
        return True
    except Exception as e:
        print(f"添加视频任务错误: {str(e)}")
        connection.rollback()
        return False
    finally:
        connection.close()