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



# ret_data = {
#     "note":{
#         "title":"文章标题",
#         "cover_img":"文章封面"
#     },
#     "msg":"查询成功",
#     "data":{
#         "ret_data":[
#             {
#                 "summary":"4oCL572R5LiK55qE5Z+L57q/5a+55q+U5Zu+5pWI5p6c5aW95Yiw5b+D5Yqo77yM5Yiw5bqV6IO95LiN6IO95YGa5ZGi77yf",
#                 "id":1285,
#                 "cover_img":"statics/img/cover_1555035227.7503235.jpg",
#                 "title":"医美经|揭开线雕的秘密"
#             },
#             {
#                 "summary":"6ZiF6K+75pys5paH5YmN77yM6K+35oKo5YWI54K55Ye75LiK6Z2i55qE6JOd6Imy5a2X5L2T4oCc6K+05oOF5oSf5LqL4oCd77yM5YaN54K55Ye74oCc5YWz5rOo4oCd77yM6L+Z5qC35oKo5bCx5Y+v5Lul57un57ut5YWN6LS55pS25Yiw5pyA5paw5paH56ug5LqG44CC5q+P5aSp6YO9",
#                 "id":1541,
#                 "cover_img":"statics/img/cover_1555293009.808119.jpg",
#                 "title":"情感故事：算了吧！放弃这段你自己所谓的“情”吧！"
#             },
#             {
#                 "summary":"44CK56ys5LqU5Lq65qC844CL5pys5ZGo5pu05paw6aKE6KeI",
#                 "id":1030,
#                 "cover_img":"statics/img/cover_1555032853.8592942.jpg",
#                 "title":"【新情报】“深渊的呼唤”主题时装终于要和大家见面啦"
#             }
#         ],
#         "count":3
#     },
#     "code":200



# price = 0.10
#
# one = float(price) * 0.3
# # one = round(one, 2)
# two = float(price) * 0.15
# # two = round(two, 2)
# print(one, two )
#
# test = '3'
#
# print(float(test) / 100)



l = ["\n", "<section class=\"_editor\"><section style:=\"margin:0px 10px;\"><section data-width=\"25%\" style=\"display: inline-block;vertical-align: middle;width: 25%;border-width: 0px;box-sizing: border-box;\"><section style=\"margin-top: 10px;margin-bottom: 10px;\"><section data-width=\"100%\" style=\"width: 100%;height: 5px;background-color: #31bf58;\"></section></section></section><section data-width=\"75%\" style=\"display: inline-block;vertical-align: middle;width: 75%;\"><section style=\"margin-top: 0.5em;margin-bottom: 0.5em;\"><section style=\"border-top: 1px dashed #31bf58;box-sizing: border-box;\"></section></section></section><p style=\"line-height: 2em;\"><span style=\"font-size: 14px;color: #979897;\">4\u670814\u65e5\u4e0b\u5348\uff0ciEnglish\u5c11\u5e74\u8bfb\u4e66\u4f1a\u5168\u56fd\u5de1\u56de\u8bb2\u5ea7\u5728\u6930\u57ce\u6d77\u53e3\u9686\u91cd\u53ec\u5f00\uff0c\u73b0\u573a\u8fd1\u767e\u4eba\u53c2\u52a0\u4f1a\u8bae\u3002</span></p><p style=\"line-height: 2em;\"><span style=\"font-size: 14px;color: #979897;\"><img class=\"\" data-ratio=\"0.6666666666666666\" src=\"http://zhugeleida.zhugeyingxiao.com/tianyan/statics/img/article_1555320751.671033.jpg\" data-type=\"jpeg\" data-w=\"1620\"/></span></p><p style=\"line-height: 2em;\"><span style=\"font-size: 14px;color: #979897;\"><img class=\"\" data-ratio=\"0.75\" src=\"http://zhugeleida.zhugeyingxiao.com/tianyan/statics/img/article_1555320751.8489878.jpg\" data-type=\"jpeg\" data-w=\"1440\"/></span></p><section style=\"text-align: right;margin-right: 0%;margin-bottom: 10px;margin-left: 0%;transform: translate3d(-16px, 0px, 0px);-webkit-transform: translate3d(-16px, 0px, 0px);-moz-transform: translate3d(-16px, 0px, 0px);-ms-transform: translate3d(-16px, 0px, 0px);-o-transform: translate3d(-16px, 0px, 0px);\"><section data-width=\"75%\" style=\"display: inline-block;vertical-align: middle;width: 75%;\"><section style=\"margin-top: 0.5em;margin-bottom: 0.5em;\"><section style=\"border-top: 1px dashed #31bf58;box-sizing: border-box;\"></section></section></section><section data-width=\"25%\" style=\"display: inline-block;vertical-align: middle;width: 25%;border-width: 0px;box-shadow: #31bf58 0px 0px 0px;box-sizing: border-box;\"><section style=\"margin-top: 10px;margin-bottom: 10px;\"><section data-width=\"100%\" style=\"width: 100%;height: 5px;background-color: #31bf58;\"></section></section></section></section></section></section>", "<p><br/></p>", "<section class=\"_editor\"><section style:=\"margin:0px 10px;\"><section data-width=\"25%\" style=\"display: inline-block;vertical-align: middle;width: 25%;border-width: 0px;box-sizing: border-box;\"><section style=\"margin-top: 10px;margin-bottom: 10px;\"><section data-width=\"100%\" style=\"width: 100%;height: 5px;background-color: #31bf58;\"></section></section></section><section data-width=\"75%\" style=\"display: inline-block;vertical-align: middle;width: 75%;\"><section style=\"margin-top: 0.5em;margin-bottom: 0.5em;\"><section style=\"border-top: 1px dashed #31bf58;box-sizing: border-box;\"></section></section></section><p style=\"line-height: 2em;\"><span style=\"font-size: 14px;color: #979897;\">\u4f1a\u4e0a\uff0c\u5317\u4eac\u8d44\u6df1\u82f1\u8bed\u6559\u80b2\u4e13\u5bb6\u3001iEnglish\u6559\u80b2\u7814\u7a76\u9662\u526f\u9662\u957f\u6768\u5149\u8001\u5e08\u7cfb\u7edf\u5730\u5206\u6790\u4e86\u5f53\u4e0b\u82f1\u8bed\u5b66\u4e60\u7684\u56f0\u5883\u6240\u5728\u3002\u4ed6\u540c\u65f6\u8868\u793a\uff0c\u82f1\u8bed\u5b66\u4e60\u7684\u76ee\u6807\u4e0d\u4ec5\u4ec5\u662f\u901a\u8fc7\u8003\u8bd5\uff0c\u800c\u662f\u8981\u5728\u65e5\u5e38\u751f\u6d3b\u4e2d\u5f97\u4ee5\u4f7f\u7528\uff0c\u80fd\u65e0\u969c\u788d\u548c\u5916\u7c4d\u4eba\u58eb\u4ea4\u6d41\u548c\u65e0\u969c\u788d\u9605\u8bfb\u82f1\u6587\u539f\u7248\u4e66\u7c4d\u3002\u6768\u5149\u8001\u5e08\u4f1a\u4e0a\u5217\u4e3e\u591a\u4e2a\u201c\u82f1\u8bed\u795e\u7ae5\u201d\u6848\u4f8b\uff0c\u6307\u51fa\u8bed\u8a00\u5b66\u4e60\u7684\u672c\u8d28\u4e0d\u662f\u80cc\u5355\u8bcd\u3001\u8bb0\u8bed\u6cd5\u3001\u80cc\u8bfe\u6587\uff0c\u800c\u662f\u8981\u8fdb\u884c\u6d77\u91cf\u7684\u590d\u6742\u573a\u666f\u4e0b\u7684\u542c\u8bfb\u8bad\u7ec3\u3002\u4ee5\u5b69\u5b50\u4e3a\u4f8b\uff0c\u57282-3\u5c81\u57fa\u672c\u90fd\u4f1a\u8bf4\u8bdd\uff0c\u5728\u6b64\u4e4b\u524d\u662f\u5bb6\u957f\u7684\u6d77\u91cf\u590d\u6742\u573a\u666f\u4e0b\u7684\u5bf9\u5b69\u5b50\u8fdb\u884c\u8bed\u8a00\u8f93\u5165\uff0c\u5b69\u5b50\u542c\u7684\u591a\u4e86\u81ea\u7136\u800c\u7136\u5c31\u4f1a\u8bf4\u3002</span></p><p style=\"line-height: 2em;\"><span style=\"font-size: 14px;color: #979897;\"><img class=\"\" data-ratio=\"0.6666666666666666\" src=\"http://zhugeleida.zhugeyingxiao.com/tianyan/statics/img/article_1555320751.9342842.jpg\" data-type=\"jpeg\" data-w=\"1620\"/></span></p><section style=\"text-align: right;margin-right: 0%;margin-bottom: 10px;margin-left: 0%;transform: translate3d(-16px, 0px, 0px);-webkit-transform: translate3d(-16px, 0px, 0px);-moz-transform: translate3d(-16px, 0px, 0px);-ms-transform: translate3d(-16px, 0px, 0px);-o-transform: translate3d(-16px, 0px, 0px);\"><section data-width=\"75%\" style=\"display: inline-block;vertical-align: middle;width: 75%;\"><section style=\"margin-top: 0.5em;margin-bottom: 0.5em;\"><section style=\"border-top: 1px dashed #31bf58;box-sizing: border-box;\"></section></section></section><section data-width=\"25%\" style=\"display: inline-block;vertical-align: middle;width: 25%;border-width: 0px;box-shadow: #31bf58 0px 0px 0px;box-sizing: border-box;\"><section style=\"margin-top: 10px;margin-bottom: 10px;\"><section data-width=\"100%\" style=\"width: 100%;height: 5px;background-color: #31bf58;\"></section></section></section></section></section></section>", "<p><br/></p>", "<section class=\"_editor\"><section style:=\"margin:0px 10px;\"><section data-width=\"25%\" style=\"display: inline-block;vertical-align: middle;width: 25%;border-width: 0px;box-sizing: border-box;\"><section style=\"margin-top: 10px;margin-bottom: 10px;\"><section data-width=\"100%\" style=\"width: 100%;height: 5px;background-color: #31bf58;\"></section></section></section><section data-width=\"75%\" style=\"display: inline-block;vertical-align: middle;width: 75%;\"><section style=\"margin-top: 0.5em;margin-bottom: 0.5em;\"><section style=\"border-top: 1px dashed #31bf58;box-sizing: border-box;\"></section></section></section><p style=\"line-height: 2em;\"><span style=\"font-size: 14px;color: #979897;\">\u4f1a\u8bae\u671f\u95f4\uff0c\u6765\u81ea\u6d77\u53e3\u7684iEnglish\u7528\u6237\u73b0\u573a\u5206\u4eab\u4e86\u4f7f\u7528\u611f\u53d7\uff0c\u540c\u65f6\u4e5f\u5411\u53c2\u4f1a\u4eba\u5458\u5c55\u793a\u4e86\u5b66\u4e60\u6210\u679c\uff0c\u6d41\u5229\u7684\u53e3\u8bed\uff0c\u6807\u51c6\u7684\u8bed\u8c03\uff0c\u8ba9\u73b0\u573a\u5bb6\u957f\u62cd\u624b\u79f0\u8d5e\u3002</span></p><p style=\"line-height: 2em;\"><span style=\"font-size: 14px;color: #979897;\"></span><img class=\"\" data-ratio=\"0.6666666666666666\" src=\"http://zhugeleida.zhugeyingxiao.com/tianyan/statics/img/article_1555320752.0126739.jpg\" data-type=\"jpeg\" data-w=\"1620\" style=\"color: rgb(151, 152, 151);font-size: 14px;\"/></p><section style=\"text-align: right;margin-right: 0%;margin-bottom: 10px;margin-left: 0%;transform: translate3d(-16px, 0px, 0px);-webkit-transform: translate3d(-16px, 0px, 0px);-moz-transform: translate3d(-16px, 0px, 0px);-ms-transform: translate3d(-16px, 0px, 0px);-o-transform: translate3d(-16px, 0px, 0px);\"><section data-width=\"75%\" style=\"display: inline-block;vertical-align: middle;width: 75%;\"><section style=\"margin-top: 0.5em;margin-bottom: 0.5em;\"><section style=\"border-top: 1px dashed #31bf58;box-sizing: border-box;\"></section></section></section><section data-width=\"25%\" style=\"display: inline-block;vertical-align: middle;width: 25%;border-width: 0px;box-shadow: #31bf58 0px 0px 0px;box-sizing: border-box;\"><section style=\"margin-top: 10px;margin-bottom: 10px;\"><section data-width=\"100%\" style=\"width: 100%;height: 5px;background-color: #31bf58;\"></section></section></section></section></section></section>", "<p><br/></p>", "<section class=\"_editor\"><section style:=\"margin:0px 10px;\"><section data-width=\"25%\" style=\"display: inline-block;vertical-align: middle;width: 25%;border-width: 0px;box-sizing: border-box;\"><section style=\"margin-top: 10px;margin-bottom: 10px;\"><section data-width=\"100%\" style=\"width: 100%;height: 5px;background-color: #31bf58;\"></section></section></section><section data-width=\"75%\" style=\"display: inline-block;vertical-align: middle;width: 75%;\"><section style=\"margin-top: 0.5em;margin-bottom: 0.5em;\"><section style=\"border-top: 1px dashed #31bf58;box-sizing: border-box;\"></section></section></section><p style=\"line-height: 2em;\"><span style=\"font-size: 14px;color: #979897;\"><img class=\"\" data-ratio=\"1\" src=\"http://zhugeleida.zhugeyingxiao.com/tianyan/statics/img/article_1555320752.0545614.jpg\" data-type=\"jpeg\" data-w=\"1500\"/></span></p><p style=\"line-height: 2em;\"><span style=\"font-size: 14px;color: #979897;\">\u4f1a\u540e\uff0c\u4e0e\u4f1a\u5bb6\u957f\u9488\u5bf9\u81ea\u8eab\u95ee\u9898\u8fdb\u884c\u4e86\u6df1\u5165\u4ea4\u6d41\uff0c\u4ed6\u4eec\u8868\u793a\uff0c\u8bed\u8a00\u5b66\u4e60\u672c\u8d28\u7684\u7406\u5ff5\u5bf9\u4e4b\u524d\u7684\u82f1\u8bed\u5b66\u4e60\u6709\u6240\u98a0\u8986\uff0c\u5982\u83b7\u81f3\u5b9d\u3002</span></p><section style=\"text-align: right;margin-right: 0%;margin-bottom: 10px;margin-left: 0%;transform: translate3d(-16px, 0px, 0px);-webkit-transform: translate3d(-16px, 0px, 0px);-moz-transform: translate3d(-16px, 0px, 0px);-ms-transform: translate3d(-16px, 0px, 0px);-o-transform: translate3d(-16px, 0px, 0px);\"><section data-width=\"75%\" style=\"display: inline-block;vertical-align: middle;width: 75%;\"><section style=\"margin-top: 0.5em;margin-bottom: 0.5em;\"><section style=\"border-top: 1px dashed #31bf58;box-sizing: border-box;\"></section></section></section><section data-width=\"25%\" style=\"display: inline-block;vertical-align: middle;width: 25%;border-width: 0px;box-shadow: #31bf58 0px 0px 0px;box-sizing: border-box;\"><section style=\"margin-top: 10px;margin-bottom: 10px;\"><section data-width=\"100%\" style=\"width: 100%;height: 5px;background-color: #31bf58;\"></section></section></section></section></section></section>", "<p><br/></p>", "<section class=\"_editor\"><p><br/></p></section>", "<p><br/></p>", "\n"]
print(
    len(l)
)








