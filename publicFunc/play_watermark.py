
from PIL import Image,ImageFont,ImageDraw
from publicFunc.account import randon_str
import os
from publicFunc.host import host_url
from publicFunc.image_color_recognition import image_color_recognition


# 图片打水印
class watermark():
    def __init__(self, data):
        self.data = data
        self.img_path = data.get('img_path')
        self.name = data.get('name')
        self.phone = data.get('phone')


    # 海报水印
    def posters_play_watermark(self):
        img_url = self.img_path.split(host_url)[1] # 切除域名
        # img_url = '1.jpg'
        image = Image.open(img_url).convert('RGBA')

        color = image_color_recognition(img_url) # 识别图片颜色 给出对应文字颜色
        # color = (0, 0, 0)

        # 绘图句柄
        image_draw = ImageDraw.Draw(image)
        posters_status = int(self.data.get('posters_status'))  # 水印类型
        text = str(self.name) + ' ' + str(self.phone)

        print('text------> ', text)
        # 正能量海报水印
        if posters_status == 1:
            print('color-----------> ', color)
            # font = ImageFont.truetype('/usr/share/fonts/chinese/msyh.ttc', 60)  # 使用自定义的字体，第二个参数表示字符大小
            font = ImageFont.truetype('/usr/share/fonts/chinese/MSYH.TTC', 40)  # 使用自定义的字体，第二个参数表示字符大小
            set_avator = self.data.get('set_avator')  # 头像
            # set_avator = '2.jpeg'
            # 获取文本大小
            name_size_x, name_size_y = image_draw.textsize(self.name, font=font)
            phone_size_x, phone_size_y = image_draw.textsize(self.phone, font=font)

            # 获取文字位置
            name_x = int((image.size[0] - name_size_x) / 2 + int(name_size_x/2))  # 名字文字左右放在居中位置
            name_y = int(image.size[1] - name_size_y - (30 + phone_size_y))  # 文字距底20像素

            phone_x = int((image.size[0] - phone_size_x) / 2 + int(name_size_x / 2))  # 电话文字左右放在居中位置
            phone_y = int(image.size[1] - phone_size_y - 20)  # 文字距底20像素

            # 设置文本位置及颜色和透明度
            image_draw.text((name_x - 50, name_y), self.name, font=font, fill=color)
            image_draw.text((phone_x - 50, phone_y), self.phone, font=font, fill=color)

            image_draw.text((50, 50), 'sdaasdasd', font=font, fill=color)
            image_draw.text((50, 100), 'sadasfsadfsxcvxz', font=font, fill=color)

            # -------------------头像--------------------------
            set_avator_image = Image.open(set_avator).convert('RGBA')
            set_avator_image.thumbnail((150, 150)) # 原比例缩放图片

            set_avator_x = int((image.size[0] - name_size_x) / 2)
            # image.paste(set_avator_image, (set_avator_x - 50, int(name_y)))
            image.paste(set_avator_image, (50, int(name_y)))

        # 邀请函海报水印
        else:
            zhu_title = self.data.get('zhu_title')
            fu_title = self.data.get('fu_title')
            time = self.data.get('time')
            place = self.data.get('place')


            text = '详询:' + text

            zhu_title_font = ImageFont.truetype('/usr/share/fonts/chinese/SIMHEI.TTF', 40)  # 使用自定义的字体，第二个参数表示字符大小
            font = ImageFont.truetype('/usr/share/fonts/chinese/SIMHEI.TTF', 30)

            zhu_title_x, zhu_title_y = image_draw.textsize(zhu_title, font=zhu_title_font)
            fu_title_x, fu_title_y = image_draw.textsize(fu_title, font=font)
            time_x, time_y = image_draw.textsize(time, font=font)
            place_x, place_y = image_draw.textsize(place, font=font)
            text_x, text_y = image_draw.textsize(text, font=font)

            zhu_title_width = int(image.size[0] / 2 - (zhu_title_x / 2))
            fu_title_width = int(image.size[0] / 2 - (fu_title_x / 2))
            time_width = int(image.size[0] / 2 - (time_x / 2))
            place_width = int(image.size[0] / 2 - (place_x / 2))
            text_width = int(image.size[0] / 2 - (text_x / 2))

            img_hight = image.size[1]
            image_draw.text((zhu_title_width, img_hight-180), zhu_title, font=zhu_title_font, fill=color)
            image_draw.text((fu_title_width, img_hight-140), fu_title, font=font, fill=color)
            image_draw.text((time_width, img_hight-110), time, font=font, fill=color)
            image_draw.text((place_width, img_hight-80), place, font=font, fill=color)
            image_draw.text((text_width, img_hight-40), text, font=font, fill=color)

        path = os.path.join('statics', 'img', randon_str() + '.png')
        image.save(path)
        return path

if __name__ == '__main__':
    img_path = '1.png'
    set_avator = '2.png'

    zhu_title = '峰会主席邀请会'
    fu_title = '期待诸位亲临现场'
    time = '2019年8月11日 上午11点'
    place = '北京one大厦23层'


    data = {
        'posters_status': 2,
        'img_path': img_path,
        'name': '微商天眼',
        'phone': 188888888,
        'set_avator': set_avator,

        'zhu_title': zhu_title,
        'fu_title': fu_title,
        'time': time,
        'place': place,
    }
    obj = watermark(data)
    poster_path = 'f045e386af4261567e8fe04169b58f82.jpg'
    logo_path = 'tianyan_logo.png'
    # obj.test(poster_path)
    obj.posters_play_watermark()






