import requests

# 图片文件路径，请根据实际情况修改
image_path = './name/1063973.JPG'

# 目标上传接口URL
url = 'http://wudichaojishuai.com/upload.php'

# 构造文件参数，键名'file'要与upload.php中$_FILES数组的键名一致
files = {'file': open(image_path, 'rb')}

try:
    # 发送POST请求上传文件
    response = requests.post(url, files=files)
    # 打印服务器返回的响应内容
    print(response.text)
except requests.exceptions.RequestException as e:
    print(f"请求发生异常: {e}")
finally:
    # 关闭文件
    files['file'].close()