import pymysql
import os
from werkzeug.security import generate_password_hash

# 配置
MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'ccl123654789*'
MYSQL_DB = os.environ.get('MYSQL_DB') or 'videogenius'


def init_db():
    """初始化数据库"""
    # 首先连接到MySQL服务器
    connection = None
    try:
        # 连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            # 检查数据库是否存在
            cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{MYSQL_DB}'")
            if not cursor.fetchone():
                # 创建数据库
                cursor.execute(f'CREATE DATABASE {MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
                print(f'数据库 {MYSQL_DB} 创建成功')

        # 关闭连接，重新连接到新创建的数据库
        connection.close()

        # 连接到新创建的数据库
        connection = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            db=MYSQL_DB,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

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
            print('用户表创建成功')

            # 检查是否已经有管理员用户
            cursor.execute('SELECT * FROM users WHERE email = %s', ('admin@example.com',))
            admin = cursor.fetchone()

            if not admin:
                # 创建管理员用户
                hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
                cursor.execute('''
                INSERT INTO users (name, email, password) VALUES (%s, %s, %s)
                ''', ('管理员', 'admin@example.com', hashed_password))
                print('管理员用户创建成功')

        connection.commit()
        print('数据库初始化完成')

    except Exception as e:
        print(f'初始化数据库时出错: {e}')
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()


if __name__ == '__main__':
    init_db()
