import os
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ...settings import IMAGE_FOLDER

GENERATE_PATH = os.path.split(os.path.realpath(__file__))[0]
template_dir = os.path.join(IMAGE_FOLDER, 'template')  # 这个路径换了


def generate_with_template(template_path, sentence):
    path = os.path.join(template_dir, template_path)
    save_path = os.path.join(IMAGE_FOLDER, "generate" + str(time.time()) + '.jpg')
    print(path, save_path)
    img = Image.open(path).convert('RGB')
    img_mat = np.asarray(img, np.uint8)
    shape = img_mat.shape
    white = np.ones((int(shape[0] / 5), shape[1], shape[2]), np.uint8) * 255
    img_con = np.concatenate((img_mat, white), axis=0)  # 连接上一块白条
    img = Image.fromarray(img_con)
    img.save(save_path)

    im = Image.open(save_path)  # .convert('RGB')

    w, h = im.size

    img_cv = cv2.imread(save_path)  # BGR格式
    cv2img = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    pilimg = Image.fromarray(cv2img)

    draw = ImageDraw.Draw(pilimg)  # 创建一个可以绘图的对象
    font_size = int(h / 6)
    if font_size * len(sentence) > w:  # 修正字体过大的问题
        font_size = int(w / len(sentence))
    font_path = os.path.join(GENERATE_PATH, "simhei.ttf")
    font = ImageFont.truetype(font_path, font_size, encoding="utf-8")
    x_pos = w / 2 - len(sentence) * font_size / 2  # 居中公式
    draw.text((x_pos, h / 6 * 5), sentence, (0, 0, 0), font=font)  # 在矩阵绘制文字
    # 我怀疑这里有问题
    # cv2charimg = cv2.cvtColor(np.array(pilimg), cv2.COLOR_RGB2BGR)#
    # cv2.imshow("ͼƬ", cv2charimg)
    # img = Image.fromarray(cv2charimg).convert('RGB')
    # img.save(save_path)
    #

    pilimg.save(save_path)

    if os.path.exists(save_path):
        return os.path.basename(save_path)
    else:
        return "write fail"

if __name__ == "__main__":
    data = generate_with_template(r'C:\Users\jnjga\Desktop\university\meme_db\SURF\after\爱豆胡歌_0.jpeg')
    print(data)
