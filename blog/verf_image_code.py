import random
from captcha.image import ImageCaptcha


def get_random_code(code, image_path):
    image = ImageCaptcha()
    image.write(code, image_path)


def generate_random_code():
    """ 随机生成4位的验证码 """
    code_list = []
    for i in range(10):  # 0-9数字
        code_list.append(str(i))
    for i in range(65, 91):  # A-Z 字母
        code_list.append(chr(i))
    for i in range(97, 123):  # a-z 字母
        code_list.append(chr(i))
    vcode = random.sample(code_list, 4)  # 从list中随机获取6个元素，作为一个片断返回
    random_code = ''.join(vcode)  # list to string
    return random_code
