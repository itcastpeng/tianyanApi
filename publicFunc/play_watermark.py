
from PIL import Image,ImageFont,ImageDraw
from publicFunc.account import randon_str
import os
from publicFunc.host import host_url
from publicFunc.image_color_recognition import image_color_recognition
import sys
from selenium import webdriver
from tianyanApi import settings
import requests
from selenium.webdriver.chrome.options import Options

# 图片打水印
class watermark():
    def __init__(self, data):
        self.data = data
        self.img_path = data.get('img_path')
        self.name = data.get('name')
        self.phone = data.get('phone')
        self.user_id = data.get('user_id')
        self.posters = data.get('posters')

    # 海报水印
    def posters_play_watermark(self):
        path = os.path.join('statics', 'poster_img', randon_str() + '.png')

        # 绘图句柄
        posters_status = int(self.data.get('posters_status'))  # 水印类型
        # color = image_color_recognition(host_url) # 识别图片颜色 给出对应文字颜色
        color = (0, 0, 0)

        # 正能量海报水印
        if posters_status == 1:
            if 'linux' in sys.platform:  # 获取平台
                base_dir_path = os.path.join(settings.BASE_DIR, 'api', 'views_dir', 'tools')
                phantomjs_path = base_dir_path + '/phantomjs'
                poster_url = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/html_oper/zhengnengliang?user_id={}&posters={}'.format(self.user_id, self.posters)
            else:
                base_dir_path = 'api/views_dir/tools'
                phantomjs_path = base_dir_path + '/phantomjs.exe'
                poster_url = 'http://127.0.0.1:8008/api/html_oper/zhengnengliang?user_id={}&posters={}'.format(self.user_id, self.posters)

            driver = webdriver.PhantomJS(executable_path=phantomjs_path)
            driver.implicitly_wait(10)
            driver.maximize_window()
            print('poster_url------------>', poster_url)
            driver.get(poster_url)
            element = driver.find_element_by_id("jietu")
            locations = element.location
            sizes = element.size
            print('locations---------> ', locations)
            print('sizes---------> ', sizes)
            # rangle = (int(locations['x']), int(locations['y']), int(locations['x'] + sizes['width']), int(locations['y'] + sizes['height']))
            print(int(locations['x'] + sizes['width']))
            print(int(locations['y'] + sizes['height']))
            rangle = (locations['x'], locations['y'], int(locations['x'] + sizes['width']), sizes['height'])
            driver.save_screenshot(path)  # 截图
            img = Image.open(path)
            jpg = img.crop(rangle) # 左上右下
            jpg.save(path)
            driver.quit()








            # name = self.name
            # phone = self.phone
            #
            # # font = ImageFont.truetype('/usr/share/fonts/chinese/Gabriola.ttf', 30)  # 使用自定义的字体，第二个参数表示字符大小
            # font = ImageFont.truetype('/usr/share/fonts/chinese/GABRIOLA.TTF', 40)  # 使用自定义的字体，第二个参数表示字符大小
            #
            # set_avator = self.data.get('set_avator')  # 头像
            # # set_avator = '2.jpeg'
            # # 获取文本大小
            #
            # name_size_x, name_size_y = image_draw.textsize(name, font=font)
            # # phone_size_x, phone_size_y = image_draw.textsize(phone, font=font)
            #
            # # 获取文字位置
            # name_x = int((image.size[0] - name_size_x) / 2)  # 名字文字左右放在居中位置
            #
            # phone_x = int(name_x + name_size_x + 10)  # 电话文字左右放在居中位置
            # phone_y = int(image.size[1] - 80)
            #
            # # 设置文本位置及颜色和透明度
            # image_draw.text((name_x, phone_y), name, font=font, fill=color)
            # image_draw.text((phone_x, phone_y), phone, font=font, fill=color)
            #
            # # -------------------头像--------------------------
            # set_avator_image = Image.open(set_avator).convert('RGBA')
            # set_avator_image.thumbnail((40, 40)) # 原比例缩放图片
            #
            # image.paste(set_avator_image, (name_x - 40, phone_y))

        # 邀请函海报水印
        else:
            img_url = self.img_path.split(host_url)[1]  # 切除域名
            image = Image.open(img_url).convert('RGBA')
            image_draw = ImageDraw.Draw(image)
            text = str(self.name) + ' ' + str(self.phone)


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






