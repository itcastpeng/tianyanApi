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


from django.shortcuts import render
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Max, Avg, F, Q, Min, Count, Sum
import datetime
import json, base64
from django.db.models import Q, Count

from bs4 import BeautifulSoup
import time
import requests
import re, os
from urllib.parse import unquote
# def deal_gzh_picture_url(leixing, url):
#     '''
#     ata-src 替换为src，将微信尾部?wx_fmt=jpeg去除
#     http://mmbiz.qpic.cn/mmbiz_jpg/icg7bNmmiaWLhUcPY7I4r6wvBFRLSTJ6L7lBRILWoKKVuvdHe4BmVxhiclQnYo2F1TDU7CcibXawl9E2n1MOicTkt6w/0?wx_fmt=jpeg

#     '''
#     # content = 'data-src="111?wx_fmt=png data-src="222?wx_fmt=jpg'
#     # phone = "2004-959-559#这是一个电话号码"
#     # # 删除注释
#     # num = re.sub(r'#.*$', "", phone)
#     # print("电话号码 : ", num)
#
#     # 移除非数字的内容
#     # url = 'https://mp.weixin.qq.com/s?__biz=MzA5NzQxODgzNw==&mid=502884331&idx=1&sn=863da48ef5bd01f5ba8ac30d45fea912&chksm=08acecd13fdb65c72e407f973c4db69a988a93a169234d2c4a95c0ca6c97054adff54c48a24f#rd'
#
# #     ret = requests.get(url)
# #
# #     ret.encoding = 'utf8'
# #
# #     soup = BeautifulSoup(ret.text, 'lxml')
# #
# #     img_tags = soup.find_all('img')
# #     for img_tag in img_tags:
# #         if img_tag.attrs.get('style'):
# #             style_list = img_tag.attrs.get('style').split(';')
# #             style_tag = ''
# #             for i in style_list:
# #                 if i and i.split(':')[0] == 'width':
# #                     style_tag = i.split(':')[1]
# #
# #             img_tag.attrs['style'] = style_tag
# #
# #         data_src = img_tag.attrs.get('data-src')
# #
# #
# #
# #
# # if __name__ == '__main__':
# #     deal_gzh_picture_url('only_url', 'https://mp.weixin.qq.com/s/dQdgO3OAIvzIOi8lmtoAog')














