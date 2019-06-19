# # from django.test import TestCase
#
# # Create your tests here.
#
#
#
#
# import re
# import requests
#
# from bs4 import BeautifulSoup
# import json, datetime, os, time
# from urllib.parse import unquote
# URL = 'http://127.0.0.1:8001/'
#
# # url = 'https://mp.weixin.qq.com/s?__biz=MzAwMTI2MDk0MQ==&mid=2798881417&idx=1&sn=d7be6d86f24a336d1f357b3954d9deb5&chksm=b9fb466b8e8ccf7ded40acadbee498b9dad18dc03eb6ddeb77c006a86ff2ee01d155da423047&xtrack=1&scene=0&subscene=131&clicktime=1552542940&ascene=7&devicetype=android-28&version=2700033b&nettype=WIFI&abtest_cookie=BQABAAgACgALABIAEwAFAJ2GHgAjlx4AVpkeAL+ZHgDWmR4AAAA=&lang=zh_CN&pass_ticket=UbMS4e8ud4NW/OpaEhFbBdzHPlEHj7N3VXAhcGfSZdrbna3jfIuVBOprYP7HO/nC&wx_header=1'
# url = 'https://mp.weixin.qq.com/s/_m1CQMd2oq0Yb9z5XvFGeg'
# ret = requests.get(url)
# ret.encoding = 'utf8'
#
# soup = BeautifulSoup(ret.text, 'lxml')
#
# title = re.compile(r'var msg_title = (.*);').findall(ret.text)[0].replace('"', '')   # 标题
# summary = re.compile(r'var msg_desc = (.*);').findall(ret.text)[0].replace('"', '')    # 摘要
# cover_url = re.compile(r'var msg_cdn_url = (.*);').findall(ret.text)[0].replace('"', '') # 封面
#
#
# s = requests.session()
# ## 把封面图片下载到本地
# now_time = int(time.time())
# html = s.get(cover_url)
# if 'wx_fmt=gif' in cover_url:
#     cover_name = "/cover_%s.gif" % (now_time)
# else:
#     cover_name = "/cover_%s.jpg" % (now_time)
#
# cover_url = os.path.join('statics', 'img') + cover_name
# with open(cover_url, 'wb') as file:
#     file.write(html.content)
#
#
# # 获取所有样式
# style = ""
# style_tags = soup.find_all('style')
# for style_tag in style_tags:
#     print('style_tag -->', style_tag)
#     style += str(style_tag)
#
# # 获取内容
# body = soup.find('div', id="js_content")
# body.attrs['style'] = "padding: 20px 16px 12px;"
# img_tags = soup.find_all('img')
# for img_tag in img_tags:
#     data_src = img_tag.attrs.get('data-src')
#     if data_src:
#
#         now_time = int(time.time())
#         html = s.get(data_src)
#
#         if 'wx_fmt=gif' in data_src:
#             img_name = "/article_%s.gif" % (now_time)
#         else:
#             img_name = "/article_%s.jpg" % (now_time)
#
#         file_dir = os.path.join('statics', 'img') + img_name
#         with open(file_dir, 'wb') as file:
#             file.write(html.content)
#         img_tag.attrs['data-src'] = URL + file_dir
#
#
# ### 处理视频的URL
# iframe = body.find_all('iframe', attrs={'class': 'video_iframe'})
#
# for iframe_tag in iframe:
#     shipin_url = iframe_tag.get('data-src')
#     data_cover_url = iframe_tag.get('data-cover')
#     if data_cover_url:
#         data_cover_url = unquote(data_cover_url, 'utf-8')
#
#     print('封面URL data_cover_url ------->>', data_cover_url)
#
#     if '&' in shipin_url and 'vid=' in shipin_url:
#         vid_num = shipin_url.split('vid=')[1]
#         _url = shipin_url.split('?')[0]
#         shipin_url = _url + '?vid=' + vid_num
#
#     iframe_tag.attrs['data-src'] = shipin_url
#     iframe_tag.attrs['allowfullscreen'] = True
#     iframe_tag.attrs['data-cover'] = data_cover_url
#
# content = str(style) + str(body)
#
# dict = {'url': '', 'data-src': 'src', '?wx_fmt=jpg': '', '?wx_fmt=png': '', '?wx_fmt=jpeg': '', '?wx_fmt=gif': '', }
# for key, value in dict.items():
#     if key == 'url':
#         pattern1 = re.compile(r'https:\/\/mmbiz.qpic.cn\/\w+\/\w+\/\w+\?\w+=\w+', re.I)  # 通过 re.compile 获得一个正则表达式对象
#         pattern2 = re.compile(r'https:\/\/mmbiz.qpic.cn\/\w+\/\w+\/\w+', re.I)
#         results_url_list_1 = pattern1.findall(content)
#         results_url_list_2 = pattern2.findall(content)
#         # print(' 匹配的微信图片链接 results_url_list_1 ---->', json.dumps(results_url_list_1))
#         # print(' 匹配的微信图片链接 results_url_list_2 ---->', json.dumps(results_url_list_2))
#         results_url_list_1.extend(results_url_list_2)
#
#         for pattern_url in results_url_list_1:
#             now_time = int(time.time())
#             ## 把图片下载到本地
#             html = s.get(pattern_url)
#             if 'wx_fmt=gif' in pattern_url:
#                 filename = "/gzh_article_%s.gif" % (now_time)
#             else:
#                 filename = "/gzh_article_%s.jpg" % (now_time)
#
#             file_dir = os.path.join('statics', 'zhugeleida', 'imgs', 'admin', 'article') + filename
#             with open(file_dir, 'wb') as file:
#                 file.write(html.content)
#
#             sub_url = URL + file_dir
#             content = content.replace(pattern_url, sub_url)
#
#     else:
#         content = content.replace(key, value)
#
# print(title, summary, cover_url, content)




# from urllib.parse import unquote
#
# print(unquote('https://www.baidu.com/s?ie=UTF-8&wd=http%253A%252F%252Fshp.qpic.cn%252Fqqvideo_ori%252F0%252Fo0876ujgqpe_496_280%252F0'))
# print(unquote('https://v.qq.com/iframe/preview.html?width=500&amp;height=375&amp;auto=0&amp;vid=o0876ujgqpe'))
#
#
# shipin_url = 'https://v.qq.com/iframe/preview.html?width=500&amp;height=375&amp;auto=0&amp;vid=o0876ujgqpe'
#
# if '&' in shipin_url and 'vid=' in shipin_url:
#     vid_num = shipin_url.split('vid=')[1]
#     _url = shipin_url.split('?')[0]
#     shipin_url = _url + '?vid=' + vid_num
# print('shipin_url->< ', shipin_url)
#
# from PIL import Image,ImageFont,ImageDraw
# from publicFunc.base64_encryption import b64decode, b64encode
# # 生成圆图
# def circle(img, path, resize):
#  ima = Image.open(img).convert("RGBA")
#  size = ima.size
#
#  # 因为是要圆形，所以需要正方形的图片
#  r2 = min(size[0], size[1])
#  if size[0] != size[1]:
#   ima = ima.resize((r2, r2), Image.ANTIALIAS)
#
#  # 最后生成圆的半径
#  r3 = 60
#  imb = Image.new('RGBA', (r3*2, r3*2),(26,172,25))
#  pima = ima.load() # 像素的访问对象
#  pimb = imb.load()
#  r = float(r2/2) #圆心横坐标
#
#  for i in range(r2):
#   for j in range(r2):
#    lx = abs(i-r) #到圆心距离的横坐标
#    ly = abs(j-r)#到圆心距离的纵坐标
#    l = (pow(lx,2) + pow(ly,2))** 0.5 # 三角函数 半径
#
#    if l < r3:
#     pimb[i-(r-r3),j-(r-r3)] = pima[i,j]
#  imb.save(path)
#
#
#
# name = '小明'
#
# huabu_x = 375   # 画布宽度
# huabu_y = 550   # 画布高度
#
# title1 = '我正在使用 微商天眼 进行'
# title2 = '客户追踪、分 享 事 业 机 会'
# title3 = '伙伴们一起来吧 !'
# title4 = '客 户 追 踪 神 器'
# title5 = '关注微商天眼公众号'
# expire_date = '有效期: 2019-05-05'
#
#
# # 新建画布纯白色           宽度↓   ↓高度    ↓ 颜色
# p = Image.new('RGBA', (huabu_x, huabu_y) , (26,172,25))
# image_draw = ImageDraw.Draw(p)
#
# font = ImageFont.truetype('/usr/share/fonts/chinese/msyhl.ttc', 18)
# font1 = ImageFont.truetype('/usr/share/fonts/chinese/msyhbd.ttc', 18)
# font2 = ImageFont.truetype('/usr/share/fonts/chinese/msyhl.ttc', 12)
# font3 = ImageFont.truetype('/usr/share/fonts/chinese/msyhl.ttc', 15)
#
# # circle('./touxiang.jpg', '2.png', (50, 50))
# touxiang_img = Image.open('./touxiang.jpg')
# touxiang_img = touxiang_img.resize((70, 70))
# p.paste(touxiang_img, (int((huabu_x - 50) / 2), 30))
# name_x, name_y = image_draw.textsize(name, font=font)
# image_draw.text((int((huabu_x - name_x) / 2) + 10, 100), name, font=font3, fill=(248,248,242))
#
# # 二维码
# erweima_img = Image.open('./erweima.jpg')
# erweima_img = erweima_img.resize((100, 100))
# p.paste(erweima_img, (huabu_x - 130, huabu_y - 130))
#
# # logo
# logo_img = Image.open('logo.png')
# logo_img = logo_img.resize((100, 100))
# p.paste(logo_img, (int((huabu_x - 100) / 2), int((huabu_y - 100) / 2)))
#
# # 左1线(粗线)
# image_draw.line(((5, 5), (5, huabu_y-5)), fill=(248,248,242), width=2)
# # 左2线(细线)
# image_draw.line(((13, 12), (13, huabu_y-13)), fill=(248,248,242), width=1)
# # 上1线
# image_draw.line(((5, 5), (huabu_x - 5, 5)), fill=(248,248,242), width=2)
# # 上2线
# image_draw.line(((13, 12), (huabu_x - 13, 12)), fill=(248,248,242), width=1)
# # 右1线
# image_draw.line(((huabu_x - 5, 5), (huabu_x - 5, huabu_y - 5)), fill=(248,248,242), width=2)
# # 右2线
# image_draw.line(((huabu_x - 13, 12), (huabu_x - 13, huabu_y - 12)), fill=(248,248,242), width=1)
# # 下1线
# image_draw.line(((5, huabu_y - 5), (huabu_x - 5, huabu_y - 5)), fill=(248,248,242), width=2)
# # 下2线
# image_draw.line(((13, huabu_y - 12), (huabu_x - 13, huabu_y - 12)), fill=(248,248,242), width=1)
#
#
# title1_x, title1_y = image_draw.textsize(title1, font=font)
# title2_x, title2_y = image_draw.textsize(title2, font=font)
# title4_x, title4_y = image_draw.textsize(title4, font=font)
#
#
# touxiangweizhi = 130 # 头像预留大小
# ziti_x = (huabu_x - title1_x) / 2 # 字体左侧位置
#
# image_draw.text((ziti_x, touxiangweizhi), title1, font=font, fill=(248,248,242))
# image_draw.text((ziti_x, touxiangweizhi + title1_y + 5), title2, font=font1, fill=(248,248,242))
# image_draw.text((ziti_x, touxiangweizhi + title1_y + title2_y + 15), title3, font=font, fill=(248,248,242))
# image_draw.text((25, huabu_y - 130), title4, font=font1, fill=(248,248,242))
# image_draw.text((25, (huabu_y - 130) + title4_y), title5, font=font2, fill=(248,248,242))
#
#
# expire_date_x, expire_date_y = image_draw.textsize(expire_date, font=font)
# print(expire_date_x)
# image_draw.text((huabu_x - 130, huabu_y - (expire_date_y / 2 + 17)), expire_date, font=font2, fill=(248,248,242))
#
#
#
# # 画箭头
# image_draw.line(((50 + title4_x, huabu_y - 130 + title4_y), (70 + title4_x, huabu_y - 130 + title4_y)), fill=(248,248,242), width=10)
# image_draw.line(((65 + title4_x,  huabu_y - 140 + title4_y), (65 + title4_x, huabu_y - 120 + title4_y)), fill=(248,248,242), width=1) #  竖线
#
# image_draw.line(((65 + title4_x,  huabu_y - 140 + title4_y), (70 + title4_x + 5, huabu_y - 130 + title4_y)), fill=(248,248,242), width=1)
# image_draw.line(((65 + title4_x,  huabu_y - 120 + title4_y), (70 + title4_x + 5, huabu_y - 130 + title4_y)), fill=(248,248,242), width=1)
#
# num_x = 65
# num_y1 = 140
# num_y2 = 120
# for i in range(10):i
#     image_draw.line(((num_x + title4_x,  huabu_y - num_y1 + title4_y), (num_x + title4_x, huabu_y - num_y2 + title4_y)), fill=(248,248,242), width=1)
#     num_x += 1
#     num_y1 -= 1
#     num_y2 += 1

p = ''

if not p :
    print('==')