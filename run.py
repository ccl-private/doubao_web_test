import os
import sys
from app import app


def run_server():
    """启动服务器"""
    try:
        # 获取端口号，默认为5000
        port = int(os.environ.get('PORT', 5005))

        # 获取主机地址，默认为0.0.0.0
        host = os.environ.get('HOST', '0.0.0.0')

        # 获取调试模式，默认为False
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'

        print(f"Starting server on {host}:{port} (debug={debug})")
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        sys.exit(1)


if __name__ == '__main__':
    run_server()
