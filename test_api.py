import requests
import json

BASE_URL = 'http://localhost:5005/api'


def test_register():
    """测试注册接口"""
    url = f'{BASE_URL}/register'
    data = {
        'name': '测试用户',
        'email': 'test@example.com',
        'password': 'password123'
    }

    response = requests.post(url, json=data)
    print('注册接口测试:')
    print(f'状态码: {response.status_code}')
    print(f'响应: {response.json()}')
    print()

    return response.status_code == 201


def test_login():
    """测试登录接口"""
    url = f'{BASE_URL}/login'
    data = {
        'email': 'test@example.com',
        'password': 'password123'
    }

    response = requests.post(url, json=data)
    print('登录接口测试:')
    print(f'状态码: {response.status_code}')
    print(f'响应: {response.json()}')
    print()

    if response.status_code == 200:
        return response.json().get('token')
    return None


def test_verify_token(token):
    """测试令牌验证接口"""
    if not token:
        print('没有有效的令牌，跳过令牌验证测试')
        return

    url = f'{BASE_URL}/verify-token'
    data = {
        'token': token
    }

    response = requests.post(url, json=data)
    print('令牌验证接口测试:')
    print(f'状态码: {response.status_code}')
    print(f'响应: {response.json()}')
    print()


def test_admin_login():
    """测试管理员登录"""
    url = f'{BASE_URL}/login'
    data = {
        'email': 'admin@example.com',
        'password': 'admin123'
    }

    response = requests.post(url, json=data)
    print('管理员登录测试:')
    print(f'状态码: {response.status_code}')
    print(f'响应: {response.json()}')
    print()


if __name__ == '__main__':
    print('开始测试API接口...\n')

    # 测试注册
    register_success = test_register()

    # 如果注册成功，测试登录
    if register_success:
        token = test_login()

        # 如果登录成功，测试令牌验证
        if token:
            test_verify_token(token)

    # 测试管理员登录
    test_admin_login()

    print('API接口测试完成')
