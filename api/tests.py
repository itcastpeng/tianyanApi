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





shipin_url = 'https://mp.weixin.qq.com/mp/readtemplate?t=pages/video_player_tmpl&action=mpvideo&auto=0&vid=wxv_800489262956412928'


if '&' in shipin_url and 'vid=' in shipin_url:
    vid_num = shipin_url.split('vid=')[1]
    _url = shipin_url.split('?')[0]
    shipin_url = _url + '?vid=' + vid_num



print('shipin_url------> ', shipin_url)



title_list = ['雷达测试文章同步', '雷达测试文章', '雷达测试同步文章2', '雷达测试文章同步1', '两次隆鼻、一次注射玻尿酸！人的鼻子到底能折腾多少次？', '没【留量】比没流量更可怕—合众康桥']
media_id_list = ['ivcZrCjmhDznUrwcjIReREEIGxlxRyrfrht82iEgw0Q', 'ivcZrCjmhDznUrwcjIReRNzPw1zYXT2aP43r0HGEj-c', 'ivcZrCjmhDznUrwcjIReRGzR15rom5lbwxRvMlHM8Vc', 'ivcZrCjmhDznUrwcjIReRPoDiI2Fke3LVhHU7hNXTXE', 'ivcZrCjmhDznUrwcjIReRKw072mb7eq1Kn9MNz7oAxA']
title = '雷达文章测试3'
media_id = 'ivcZrCjmhDznUrwcjIReRNzPw1zYXT2aP43r0HGEj-c'

if (title not in title_list) or (media_id not in media_id_list): # 如果不存在创建
    print('========')

from publicFunc import  account

print(account.str_encrypt(123))











