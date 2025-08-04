from pyzbar.pyzbar import decode
from PIL import Image

def read_qr_code(image_path):
    try:
        # 打开图片
        image = Image.open(image_path)
        # 解码图片中的二维码
        decoded_objects = decode(image)
        if decoded_objects:
            # 遍历解码结果
            for obj in decoded_objects:
                # 获取二维码中的数据并解码为字符串
                qr_data = obj.data.decode('utf-8')
                return qr_data
        else:
            return "未在图片中找到二维码。"
    except Exception as e:
        return f"发生错误: {str(e)}"

# 调用函数并传入图片路径
image_path = './img/20250216211912.jpg'
result = read_qr_code(image_path)
print(result)