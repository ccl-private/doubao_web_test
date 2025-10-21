# VideoGenius 后端 API (简化版)

这是一个简化版的VideoGenius后端API，用于处理注册登录功能。这个版本不使用Flask-SQLAlchemy，而是直接使用PyMySQL来连接和操作数据库，以解决Python 3.13下的兼容性问题。

## 功能特点

- 用户注册
- 用户登录
- JWT令牌验证
- 跨域资源共享(CORS)支持

## 技术栈

- Python 3.8+ (兼容Python 3.13)
- Flask 2.3+
- Flask-CORS 4.0+
- PyJWT 2.8+
- PyMySQL 1.1+
- MySQL

## 安装步骤

1. 克隆项目

```bash
git clone <repository-url>
cd videogenius-backend
```

2. 创建虚拟环境并激活

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖

```bash
pip install -r requirements_simple.txt
```

4. 配置数据库

- 确保MySQL服务器已运行
- 修改配置文件或设置环境变量来配置数据库连接信息

5. 初始化数据库

```bash
python init_db_simple.py
```

6. 运行应用

```bash
python run_simple.py
```

## API 接口

### 注册

- URL: `/api/register`
- 方法: POST
- 请求体:
  ```json
  {
    "name": "用户名",
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- 响应:
  ```json
  {
    "message": "注册成功"
  }
  ```

### 登录

- URL: `/api/login`
- 方法: POST
- 请求体:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- 响应:
  ```json
  {
    "message": "登录成功",
    "token": "jwt-token",
    "user": {
      "id": 1,
      "name": "用户名",
      "email": "user@example.com"
    }
  }
  ```

### 验证令牌

- URL: `/api/verify-token`
- 方法: POST
- 请求体:
  ```json
  {
    "token": "jwt-token"
  }
  ```
- 响应:
  ```json
  {
    "message": "令牌有效",
    "user": {
      "id": 1,
      "name": "用户名",
      "email": "user@example.com"
    }
  }
  ```

## 配置说明

可以通过以下环境变量来配置应用:

- `SECRET_KEY`: 用于JWT加密的密钥
- `MYSQL_HOST`: MySQL服务器地址
- `MYSQL_USER`: MySQL用户名
- `MYSQL_PASSWORD`: MySQL密码
- `MYSQL_DB`: 数据库名称
- `PORT`: 服务器端口号
- `HOST`: 服务器主机地址
- `DEBUG`: 是否启用调试模式

## 注意事项

- 生产环境中请使用强密钥，并通过环境变量设置
- 生产环境中请关闭DEBUG模式
- 不要在生产环境中使用root用户连接数据库
- 定期备份数据库