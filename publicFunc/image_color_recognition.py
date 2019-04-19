from PIL import Image,ImageFont,ImageDraw
import colorsys

# 识别图片颜色
def image_color_recognition(img_url):
    if 'http://zhugeleida.zhugeyingxiao.com/tianyan/' in img_url:
        img_url = img_url.replace('http://zhugeleida.zhugeyingxiao.com/tianyan/', '')
    image = Image.open(img_url).convert('RGBA')
    image.thumbnail((50, 50))
    max_score = 0
    dominant_color = None

    for count, (r, g, b, a) in image.getcolors(image.size[0] * image.size[1]):
        # 跳过纯黑色
        if a == 0:
            continue
        saturation = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)[1]
        y = min(abs(r * 2104 + g * 4130 + b * 802 + 4096 + 131072) >> 13, 235)
        y = (y - 16.0) / (235 - 16)
        # 忽略高亮色
        if y > 0.9:
            continue

        score = (saturation + 0.1) * count
        if score > max_score:
            max_score = score
            dominant_color = (r, g, b)

    print('dominant_color------> ', type(dominant_color), dominant_color)

    r = dominant_color[0]
    g = dominant_color[1]
    b = dominant_color[2]
    color = (248,248,242) # 白色  默认颜色

    if r >= 150 and g >= 150 and b >= 150:
        color = (0, 0, 0) # 黑色

    return color


if __name__ == '__main__':
    path = 'f045e386af4261567e8fe04169b58f82.jpg'
    print('path--> ', path)
    image = Image.open(path).convert('RGBA')
    image_color_recognition(image)
