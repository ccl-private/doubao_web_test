import json
from urllib import request
from typing import Tuple


def load_prompt_template(template_path: str) -> dict:
    """加载提示词模板"""
    with open(template_path, "r", encoding="utf-8") as f:
        return json.load(f)


def submit_comfyui_task(
        prompt_template: dict,
        comfyui_url: str,
        image_path: str,
        positive_prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        length: int,
        fps: int,
        filename_prefix: str
) -> Tuple[bool, str, str]:
    """
    提交任务到ComfyUI

    Args:
        prompt_template: 提示词模板字典
        comfyui_url: ComfyUI的prompt接口URL
        image_path: 输入图片路径
        positive_prompt: 正面提示词
        negative_prompt: 负面提示词
        width: 视频宽度
        height: 视频高度
        length: 视频长度(帧)
        fps: 帧率
        filename_prefix: 输出文件名前缀

    Returns:
        (是否成功, prompt_id, 错误信息)
    """
    try:
        # 复制模板以避免修改原始模板
        prompt = json.loads(json.dumps(prompt_template))

        # 设置输入图像
        prompt["97"]["inputs"]["image"] = image_path

        # 设置正面提示词
        prompt["93"]["inputs"]["text"] = positive_prompt

        # 设置负面提示词
        prompt["89"]["inputs"]["text"] = negative_prompt

        # 设置视频参数
        prompt["98"]["inputs"]["width"] = width
        prompt["98"]["inputs"]["height"] = height
        prompt["98"]["inputs"]["length"] = length

        # 设置帧率
        prompt["94"]["inputs"]["fps"] = fps

        # 设置输出文件名
        prompt["108"]["inputs"]["filename_prefix"] = filename_prefix

        # 构建请求
        payload = {"prompt": prompt}
        data = json.dumps(payload).encode("utf-8")

        req = request.Request(
            comfyui_url,
            data=data,
            headers={"Content-Type": "application/json"}
        )

        # 发送请求
        response = request.urlopen(req)
        result = json.loads(response.read())

        if "prompt_id" in result:
            return True, result["prompt_id"], ""
        else:
            return False, "", f"ComfyUI响应不包含prompt_id: {str(result)}"

    except Exception as e:
        return False, "", f"提交任务失败: {str(e)}"


if __name__ == "__main__":
    """测试ComfyUI任务提交功能"""
    import time

    # 测试配置
    TEMPLATE_PATH = "video_wan2_2_14B_i2v.json"
    COMFYUI_URL = "http://192.168.2.158:8188/prompt"  # 可替换为实际的ComfyUI地址
    TEST_IMAGE_PATH = "/home/ccl/Pictures/Screenshot_2024-12-06_16-54-16.png"
    TEST_POSITIVE_PROMPT = "测试视频生成"
    TEST_NEGATIVE_PROMPT = "'色调艳丽，过曝，静态，细节模糊不清'"
    TEST_WIDTH = 640
    TEST_HEIGHT = 640
    TEST_LENGTH = 81
    TEST_FPS = 16
    TEST_FILENAME_PREFIX = f"video/test_{int(time.time())}"

    try:
        print("加载提示词模板...")
        template = load_prompt_template(TEMPLATE_PATH)

        print("提交测试任务到ComfyUI...")
        success, prompt_id, error = submit_comfyui_task(
            prompt_template=template,
            comfyui_url=COMFYUI_URL,
            image_path=TEST_IMAGE_PATH,
            positive_prompt=TEST_POSITIVE_PROMPT,
            negative_prompt=TEST_NEGATIVE_PROMPT,
            width=TEST_WIDTH,
            height=TEST_HEIGHT,
            length=TEST_LENGTH,
            fps=TEST_FPS,
            filename_prefix=TEST_FILENAME_PREFIX
        )

        if success:
            print(f"任务提交成功！prompt_id: {prompt_id}")
        else:
            print(f"任务提交失败: {error}")

    except Exception as e:
        print(f"测试过程出错: {str(e)}")
