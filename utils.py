import base64
import os
import time

# 图片保存目录（自动创建）
IMAGE_SAVE_DIR = "uploaded_images"
os.makedirs(IMAGE_SAVE_DIR, exist_ok=True)


def save_base64_image(base64_str: str, email: str) -> tuple[bool, str, str]:
    """保存Base64图片到本地，返回保存路径"""
    try:
        # 验证图片格式
        supported_formats = ('data:image/jpeg;base64,', 'data:image/png;base64,', 'data:image/webp;base64,')
        if not base64_str.startswith(supported_formats):
            return False, "", "不支持的图片格式（仅支持jpeg/png/webp）"

        # 提取格式和Base64数据
        format_prefix = base64_str.split(';base64,')[0]
        image_format = format_prefix.split('/')[-1]  # 如 'png'
        base64_data = base64_str.split(';base64,')[1]

        # 生成唯一文件名：邮箱（处理特殊字符）+ 毫秒时间戳 + 格式
        safe_email = email.replace('@', '_').replace('.', '_')
        timestamp = int(time.time() * 1000)
        filename = f"{safe_email}_{timestamp}.{image_format}"
        save_path = os.path.join(IMAGE_SAVE_DIR, filename)

        # 解码并保存
        image_data = base64.b64decode(base64_data)
        with open(save_path, 'wb') as f:
            f.write(image_data)

        return True, save_path, ""

    except Exception as e:
        return False, "", f"图片保存失败: {str(e)}"