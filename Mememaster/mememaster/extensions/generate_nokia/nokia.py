import os, time
from collections import deque
from PIL import Image, ImageFont, ImageDraw
from ...settings import IMAGE_FOLDER

font_size = 70
line_gap = 20
body_pos = (205, 340)
subtitle_pos = (790, 320)
body_color = (0, 0, 0, 255)
subtitle_color = (129, 212, 250, 255)
line_rotate = -9.8
max_line_width = 680
this_dir = os.path.dirname(__file__)
font = ImageFont.truetype(os.path.join(this_dir,"fonts/1.ttf"), font_size)


def draw_subtitle(im, text: str):
    width, height = font.getsize(text)
    image2 = Image.new("RGBA", (width, height))
    draw2 = ImageDraw.Draw(image2)
    draw2.text((0, 0), text=text, font=font, fill=subtitle_color)
    image2 = image2.rotate(line_rotate, expand=1)

    px, py = subtitle_pos
    sx, sy = image2.size
    im.paste(image2, (px, py, px + sx, py + sy), image2)


def generate_nokia(text: str):
    save_path = os.path.join(IMAGE_FOLDER, "诺基亚有内鬼短信" + text + str(time.time()) + '.jpg')

    im = Image.open(os.path.join(this_dir, "images/3.png"))
    length = len(text)
    width, height = font.getsize(text)
    current_width = 0
    lines = []
    line = ""
    q = deque(text)

    while q:
        word = q.popleft()
        width, _ = font.getsize(word)
        current_width += width
        if current_width >= max_line_width:
            q.appendleft(word)
            lines.append(line)
            current_width = 0
            line = ""
        else:
            line += word
    lines.append(line)
    image2 = Image.new("RGBA", (max_line_width, 450))
    draw2 = ImageDraw.Draw(image2)
    for i, line in enumerate(lines):
        draw2.text((0, i * (height + line_gap)), text=line, font=font, fill=body_color)
    image2 = image2.rotate(line_rotate, expand=1)

    px, py = body_pos
    sx, sy = image2.size
    im.paste(image2, (px, py, px + sx, py + sy), image2)
    draw_subtitle(im, f"{length}/900")
    im.save(save_path, "png")

    if os.path.exists(save_path):
        return os.path.basename(save_path)
    else:
        return "write fail"
