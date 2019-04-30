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

p = ["\n", "<section class=\"xmteditor\" data-label=\"powered by xmt.cn\" data-tools=\"\u65b0\u5a92\u4f53\u7ba1\u5bb6\" style=\"display:none;\"></section>", "<section class=\"xmteditor\" data-label=\"powered by xmt.cn\" data-tools=\"\u65b0\u5a92\u4f53\u7ba1\u5bb6\" style=\"display:none;\"></section>", "<section class=\"xmteditor\" data-label=\"powered by xmt.cn\" data-tools=\"\u65b0\u5a92\u4f53\u7ba1\u5bb6\" style=\"display:none;\"></section>", "<section class=\"xmteditor\" data-label=\"powered by xmt.cn\" data-tools=\"\u65b0\u5a92\u4f53\u7ba1\u5bb6\" style=\"display:none;\"></section>", "<p style=\"max-width: 100%;min-height: 1em;letter-spacing: 0.544px;white-space: normal;outline: none;box-sizing: border-box !important;word-wrap: break-word !important;\"><img class=\"__bg_gif\" data-backh=\"102\" data-backw=\"654\" data-before-oversubscription-url=\"https://mmbiz.qpic.cn/mmbiz_gif/FqY4f41EBWcfia4AyZX7LtgyLnfZqDGhQyMr852ickTc8g2XJwXiaUbunAQGpZYibqkkh0DxHTM27oBvhibex7QPE1A/\" data-copyright=\"0\" data-ratio=\"0.15644171779141106\" src=\"http://zhugeleida.zhugeyingxiao.com/tianyan/statics/img/article_1554970281.7918923.gif\" data-type=\"gif\" data-w=\"652\" style=\"border-width: 0px;border-style: initial;border-color: initial;letter-spacing: 0.544px;text-align: center;background-color: rgb(255, 255, 255);width: 100%;box-sizing: border-box !important;overflow-wrap: break-word !important;visibility: visible !important;height: auto;\"/></p>", "<p style=\"text-align: center;\"><img class=\"\" data-backh=\"262\" data-backw=\"500\" data-before-oversubscription-url=\"https://mmbiz.qpic.cn/mmbiz_gif/FqY4f41EBWdCHy06xkicFCc7VwTHRx7RicvEBQFVicqNdFTn95icELMr3qQCzAibI3s0icq4ZL8yQTUJqgOCNnTYjicgA/\" data-copyright=\"0\" data-ratio=\"0.524\" src=\"http://zhugeleida.zhugeyingxiao.com/tianyan/statics/img/article_1554970281.8551075.gif\" data-type=\"gif\" data-w=\"500\" style=\"width: 100%;height: auto;\"/></p>", "<p><mpvoice class=\"res_iframe js_editor_audio audio_iframe place_audio_area\" frameborder=\"0\" high_size=\"3361.9\" isaac2=\"1\" low_size=\"845.72\" name=\"\u548c\u6b63\u80fd\u91cf\u7684\u4eba\u5728\u4e00\u8d77\uff0c\u771f\u7684\u5f88\u91cd\" play_length=\"430000\" source_size=\"845.7\" src=\"/cgi-bin/readtemplate?t=tmpl/audio_tmpl&amp;name=%E5%92%8C%E6%AD%A3%E8%83%BD%E9%87%8F%E7%9A%84%E4%BA%BA%E5%9C%A8%E4%B8%80%E8%B5%B7%EF%BC%8C%E7%9C%9F%E7%9A%84%E5%BE%88%E9%87%8D&amp;play_length=07:10\" voice_encode_fileid=\"MjM5OTIxMzc4Ml8yNjUxOTY1MDg5\"></mpvoice></p>", "<p style=\"max-width: 100%;min-height: 1em;letter-spacing: 0.544px;white-space: normal;outline: none;text-align: center;box-sizing: border-box !important;word-wrap: break-word !important;\"><span style=\"max-width: 100%;background-color: rgb(255, 255, 255);color: rgb(151, 173, 172);font-family: \u5fae\u8f6f\u96c5\u9ed1;font-size: 12px;letter-spacing: 1px;white-space: pre-wrap;widows: 1;box-sizing: border-box !important;word-wrap: break-word !important;\">\u70b9\u4e0a\u65b9\u7eff\u6807\u5373\u53ef\u6536\u542c\u4e3b\u64ad\u4e9a\u6960\u6717\u8bfb\u97f3\u9891</span><br style=\"max-width: 100%;box-sizing: border-box !important;word-wrap: break-word !important;\"/></p>", "<p style=\"max-width: 100%;min-height: 1em;letter-spacing: 0.544px;white-space: normal;outline: none;text-align: right;line-height: normal;box-sizing: border-box !important;word-wrap: break-word !important;\"><span style=\"max-width: 100%;color: rgb(136, 136, 136);font-size: 12px;box-sizing: border-box !important;word-wrap: break-word !important;\">\u6765\u6e90 |\u00a0</span><span style=\"color: rgb(136, 136, 136);font-size: 12px;letter-spacing: 0.544px;text-align: center;background-color: rgb(255, 255, 255);\">\u591c</span><span style=\"max-width: 100%;color: rgb(136, 136, 136);font-size: 12px;box-sizing: border-box !important;word-wrap: break-word !important;\">\u542c\u597d\u4e66</span></p>", "<p style=\"max-width: 100%;min-height: 1em;letter-spacing: 0.544px;white-space: normal;outline: none;text-align: right;line-height: normal;box-sizing: border-box !important;word-wrap: break-word !important;\"><span style=\"max-width: 100%;color: rgb(136, 136, 136);font-size: 12px;box-sizing: border-box !important;word-wrap: break-word !important;\">ID\uff1aC9889C</span></p>", "<p><br/></p>", "<section data-role=\"outer\" label=\"Powered by 135editor.com\"><p style=\"text-align: center;margin-bottom: 5px;\"><span style=\"color: rgb(0, 0, 0);\"><strong>- 01 -</strong></span></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u4ee5\u524d\u6d41\u4f20\u7740\u8fd9\u6837\u4e00\u4e2a\u6545\u4e8b\uff1a</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u4e00\u4f4d\u8001\u5a46\u5a46\uff0c\u6709\u4e24\u4e2a\u513f\u5b50\uff0c\u5927\u513f\u5b50\u5356\u8349\u978b\uff0c\u5c0f\u513f\u5b50\u5356\u96e8\u4f1e\u3002\u6240\u4ee5\uff0c\u4e0d\u7ba1\u662f\u6674\u5929\u8fd8\u662f\u96e8\u5929\uff0c\u8001\u5a46\u5a46\u90fd\u6101\u7709\u4e0d\u5c55\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u90bb\u5c45\u4e00\u5c0f\u5ab3\u5987\uff0c\u89c1\u5979\u6574\u65e5\u54c0\u58f0\u53f9\u6c14\u7684\uff0c\u5c31\u95ee\u5979\u4e3a\u4ec0\u4e48\u4e0d\u9ad8\u5174\uff1f</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u5979\u8bf4\uff1a\u201c\u96e8\u5929\u62c5\u5fc3\u5927\u513f\u5b50\u7684\u8349\u978b\u5356\u4e0d\u51fa\u53bb\uff0c\u6674\u5929\u53c8\u62c5\u5fc3\u5c0f\u513f\u5b50\u7684\u96e8\u4f1e\u6ca1\u4eba\u4e70\u3002\u201d</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u5c0f\u5ab3\u5987\u4e00\u542c\uff0c\u5b89\u6170\u5979\u8bf4\uff1a</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u8fd9\u4e0d\u5f88\u597d\u561b\uff0c\u4e0d\u7ba1\u662f\u4ec0\u4e48\u65e5\u5b50\uff0c\u4ed6\u4eec\u5bb6\u90fd\u6709\u94b1\u6536\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u8001\u5a46\u5a46\u4e00\u60f3\uff0c\u662f\u8fd9\u4e48\u56de\u4e8b\uff0c\u4ece\u6b64\u4e4b\u540e\u5c31\u4e50\u5475\u5475\u7684\u4e86\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u6545\u4e8b\u7b80\u5355\uff0c\u9053\u7406\u4e5f\u7b80\u5355\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u79ef\u6781\u4e50\u89c2\u7684\u4eba\uff0c\u770b\u5f85\u95ee\u9898\u6c38\u8fdc\u90fd\u4f1a\u5148\u5f80\u597d\u7684\u65b9\u5411\u60f3\uff0c\u800c\u60b2\u89c2\u7684\u4eba\uff0c\u5374\u603b\u662f\u5148\u770b\u5230\u9ed1\u6697\u7684\u4e00\u9762\u3002</span></p><p><br/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u81ea\u53e4\uff0c\u7269\u4ee5\u7c7b\u805a\uff0c\u4eba\u4ee5\u7fa4\u5206\u3002<br/></span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u79d1\u5b66\u5bb6\u7814\u7a76\u8868\u660e\uff1a</span></p><p><br style=\"max-width: 100%;\"/></p><blockquote><p style=\"letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;line-height: 1.5em;\"><span style=\"font-size: 14px;color: rgb(136, 136, 136);\">\u4eba\u662f\u60df\u4e00\u80fd\u63a5\u53d7\u6697\u793a\u7684\u52a8\u7269\u3002</span></p></blockquote><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u4f60\u9009\u62e9\u548c\u4ec0\u4e48\u6837\u7684\u4eba\u5728\u4e00\u8d77\uff0c\u6162\u6162\u5730\u4f60\u5c31\u4f1a\u53d8\u6210\u8ddf\u4ed6\u4e00\u6837\u7684\u4eba\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u6f5c\u79fb\u9ed8\u5316\u7684\u529b\u91cf\u548c\u8033\u6fe1\u76ee\u67d3\u7684\u4f5c\u7528\uff0c\u771f\u7684\u4e0d\u80fd\u5ffd\u89c6\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"color: rgb(0, 0, 0);\"><strong><span style=\"font-size: 15px;\">\u575a\u6301\u548c\u6b63\u80fd\u91cf\u7684\u4eba\u5728\u4e00\u8d77\uff0c\u4e45\u800c\u4e45\u4e4b\uff0c\u4f60\u7684\u5185\u5fc3\u4e5f\u4f1a\u5145\u6ee1\u5c0f\u592a\u9633\u3002</span></strong></span></p><p><br/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><img class=\"\" data-backh=\"354\" data-backw=\"638\" data-before-oversubscription-url=\"https://mmbiz.qpic.cn/mmbiz_jpg/FqY4f41EBWcOIMFNJZfYzeRBPd6mTQzXbgc2icNssQeAicgJvx1BS5GH1ClalA97oiaJxTw2vqclrcNzjsQqNvsrQ/\" data-copyright=\"0\" data-ratio=\"0.5555555555555556\" data-s=\"300,640\" src=\"http://zhugeleida.zhugeyingxiao.com/tianyan/statics/img/article_1554970281.9040809.jpg\" data-type=\"jpeg\" data-w=\"900\" style=\"text-align: center;width: 100%;height: auto;\"/></p><p><br/></p><p style=\"text-align: center;margin-bottom: 5px;\"><span style=\"color: rgb(0, 0, 0);\"><strong>- 02 -</strong></span></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u8d75\u5a7650\u6765\u5c81\uff0c\u662f\u4e2a\u81ea\u6765\u719f\u7684\u4eba\uff0c\u521a\u642c\u6765\u5c0f\u533a\u90a3\u4f1a\uff0c\u8c01\u4e5f\u4e0d\u8ba4\u8bc6\uff0c\u5979\u4e5f\u80fd\u8fc7\u53bb\u51d1\u4e2a\u70ed\u95f9\uff0c\u62c9\u62c9\u5bb6\u5e38\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u767d\u5929\u5fd9\u7740\u5e26\u5a03\u505a\u996d\uff0c\u665a\u4e0a\u4e00\u5f97\u7a7a\u4e86\u5c31\u5230\u697c\u5e95\u4e0b\u7eb3\u51c9\u804a\u5929\uff0c\u6309\u7406\u8bf4\uff0c\u662f\u5f88\u60ec\u610f\u7684\u4e00\u4ef6\u4e8b\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u4f46\u662f\uff0c\u5979\u6bcf\u6b21\u804a\u7740\u804a\u7740\u5c31\u5f80\u81ea\u5df1\u8eab\u4e0a\u5e26\uff0c\u7136\u540e\u5f00\u59cb\u548c\u4eba\u8bf4\u5979\u7684\u4e0d\u6613\uff0c\u8bf4\u5979\u7684\u59d4\u5c48\uff0c\u8bf4\u5979\u7684\u513f\u5ab3\u5987\u662f\u600e\u4e48\u600e\u4e48\u7684\u4e0d\u597d\uff0c\u4e00\u809a\u5b50\u7684\u6028\u6c14\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u8d77\u521d\uff0c\u548c\u5979\u804a\u5929\u7684\u4eba\uff0c\u4e5f\u6ca1\u89c9\u5f97\u4ec0\u4e48\uff0c\u5c31\u5f53\u65b0\u9c9c\u4e8b\uff0c\u542c\u542c\u4e50\u5b50\uff0c\u5076\u5c14\u4ee5\u201c\u8fc7\u6765\u4eba\u201d\u7684\u89d2\u8272\u5f00\u5bfc\u5979\u4e00\u4e0b\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u65f6\u95f4\u957f\u4e86\uff0c\u53d1\u73b0\u6bcf\u5929\u5c31\u90a3\u4e48\u51e0\u4ef6\u4e0d\u987a\u5fc3\u7684\u4e8b\uff0c\u98a0\u6765\u5012\u53bb\u7684\u57cb\u6028\uff0c\u602a\u8fd9\u602a\u90a3\uff0c\u529d\u4e5f\u6ca1\u7528\uff0c\u5979\u603b\u4f1a\u7acb\u9a6c\u63a5\u8bdd\u5426\u5b9a\u4f60\uff0c\u544a\u8bc9\u4f60\u6ca1\u7528\uff0c\u7136\u540e\u7ee7\u7eed\u5410\u82e6\u6c34\uff0c\u8d1f\u80fd\u91cf\u7206\u68da\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u548c\u5979\u6bd4\u8f83\u719f\u7684\u51e0\u4f4d\u90bb\u5c45\u542c\u70e6\u4e86\uff0c\u5c31\u4f1a\u6709\u610f\u65e0\u610f\u5730\u758f\u79bb\u5979\uff0c\u4e8e\u662f\uff0c\u5979\u4eec\u4e5f\u6210\u4e86\u88ab\u62b1\u6028\u7684\u5bf9\u8c61\u3002</span></p><p><br/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u5c0f\u533a\u5c31\u8fd9\u4e48\u70b9\u5927\uff0c\u8fd9\u4e8b\u4e00\u4f20\u51fa\u53bb\uff0c\u53ea\u8981\u662f\u7ecf\u5e38\u5728\u697c\u5e95\u4e0b\u6d3b\u52a8\u7684\u90bb\u5c45\u90fd\u4f1a\u77e5\u9053\uff0c\u6709\u8d75\u5a76\u8fd9\u4e48\u4e00\u53f7\u4eba\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"color: rgb(0, 0, 0);\"><strong><span style=\"font-size: 15px;\">\u5fc3\u91cc\u4e0d\u6ee1\u7684\u4eba\uff0c\u53ea\u8981\u902e\u7740\u673a\u4f1a\u5c31\u4f1a\u5411\u4eba\u503e\u8bc9\u3002</span></strong></span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u8fd9\u4e0d\uff0c\u8d75\u5a76\u524d\u6bb5\u65f6\u95f4\u5929\u5929\u90fd\u5750\u5728\u82b1\u575b\u8fb9\u4e0a\u8ddf\u4e00\u4e2a\u5934\u53d1\u82b1\u767d\u7684\u8001\u4eba\u5bb6\u804a\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u51e0\u4e2a\u6708\u4e4b\u540e\uff0c\u771f\u7684\u6709\u53d8\u5316\u3002<br style=\"max-width: 100%;\"/></span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u8d75\u5a76\u867d\u7136\u5076\u5c14\u8fd8\u662f\u4f1a\u6709\u70b9\u62b1\u6028\uff0c\u4f46\u4e0d\u518d\u603b\u662f\u5ff5\u53e8\u90a3\u4e9b\u7834\u829d\u9ebb\u70c2\u8c37\u5b50\u7684\u70e6\u5fc3\u4e8b\uff0c\u4e5f\u4e0d\u518d\u662f\u90a3\u4e2a\u95f9\u4eba\u7684\u6028\u5987\u4e86\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u8bf4\u8d77\u6765\uff0c\u8fd8\u771f\u5f97\u611f\u8c22\u8fd9\u4f4d\u8001\u4eba\u5bb6\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u8d75\u5a76\u8bf4\uff0c\u770b\u7740\u4e50\u89c2\u53c8\u7cbe\u795e\u6296\u64de\u7684\u8001\u4eba\u5bb6\uff0c\u81ea\u5df1\u6709\u70b9\u60ed\u6127\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u5979\u6bcf\u5929\u8ddf\u7740\u8001\u4eba\u5bb6\uff0c\u8fb9\u804a\u8fb9\u6563\u6b65\uff0c\u8fd8\u65f6\u4e0d\u65f6\u80fd\u542c\u5230\u4e00\u4e9b\u5b89\u6170\u9f13\u52b1\u7684\u8bdd\uff0c\u8ba9\u5979\u51e1\u4e8b\u770b\u5f00\u4e9b\uff0c\u5c11\u70b9\u8ba1\u8f83\uff0c\u522b\u81ea\u5df1\u8ddf\u81ea\u5df1\u8fc7\u610f\u4e0d\u53bb\u3002</span></p><p><br/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><img class=\"\" data-backh=\"354\" data-backw=\"638\" data-before-oversubscription-url=\"https://mmbiz.qpic.cn/mmbiz_jpg/FqY4f41EBWcOIMFNJZfYzeRBPd6mTQzXlYV3LPbmDYPsqQZpUfM8sZ5ol35JO5P9Nu1ssnupWku0zsP6Be7lkA/\" data-copyright=\"0\" data-ratio=\"0.5555555555555556\" data-s=\"300,640\" src=\"http://zhugeleida.zhugeyingxiao.com/tianyan/statics/img/article_1554970282.0120473.jpg\" data-type=\"jpeg\" data-w=\"900\" style=\"text-align: center;width: 100%;height: auto;\"/></p><p><br/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u4eba\u8001\u4e86\uff0c\u4e0d\u6c42\u522b\u7684\uff0c\u5c31\u6c42\u4e2a\u5065\u5eb7\u81ea\u5728\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"color: rgb(0, 0, 0);\"><strong><span style=\"font-size: 15px;\">\u8c01\u90fd\u6709\u70e6\u607c\uff0c\u8c01\u90fd\u4f1a\u9047\u5230\u96be\u4e8b\uff0c\u53ea\u4e0d\u8fc7\u4e50\u89c2\u7684\u4eba\u5c11\u4e9b\u62b1\u6028\uff0c\u591a\u4e9b\u884c\u52a8\uff0c\u8ddf\u8fd9\u6837\u7684\u4eba\u5728\u4e00\u8d77\u4e45\u4e86\uff0c\u81ea\u7136\u800c\u7136\u4e5f\u4f1a\u5145\u6ee1\u6b63\u80fd\u91cf\u3002</span></strong></span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"text-align: center;margin-bottom: 5px;\"><span style=\"color: rgb(0, 0, 0);\"><strong>- 03 -</strong></span></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u5b63\u7fa1\u6797\u8001\u5148\u751f\u53ef\u4ee5\u8bf4\u662f\u770b\u6de1\u4eba\u751f\u7684\u5178\u8303\u4e86\uff0c\u665a\u5e74\u4e5f\u6d3b\u5728\u5185\u5fc3\u7684\u8212\u5fc3\u60ec\u610f\u4e2d\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u4ed6\u66fe\u8bf4\u8fc7\uff1a</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u4eba\u751f\u4e0d\u5982\u610f\u4e8b\uff0c\u5341\u4e4b\u516b\u4e5d\uff0c\u5e38\u60f3\u4e00\u4e8c\u3002</span></p><p><br/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u5982\u679c\u6574\u65e5\u7ea0\u7ed3\u90a3\u516b\u4e5d\u4e0d\u653e\uff0c\u80af\u5b9a\u662f\u5feb\u4e50\u4e0d\u8d77\u6765\u7684\uff0c\u53ea\u4f1a\u8ba9\u81ea\u5df1\u6d88\u6781\u632b\u8d25\uff0c\u9677\u5165\u4e00\u4e2a\u6b7b\u80e1\u540c\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u76f8\u53cd\uff0c\u5e38\u5e38\u628a\u773c\u5149\u653e\u5728\u90a3\u4e00\u4e8c\u7684\u5c0f\u786e\u5e78\u4e0a\uff0c\u6574\u4e2a\u4eba\u90fd\u4f1a\u5145\u6ee1\u6b63\u80fd\u91cf\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u6709\u53e5\u8bdd\u8bf4\u5f97\u597d\uff0c\u4f60\u5f88\u91cd\u8981\uff0c\u4f46\u548c\u8c01\u5728\u4e00\u8d77\u66f4\u91cd\u8981\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u4e00\u4e2a\u4eba\u6700\u7ec8\u4f1a\u8d70\u5411\u4f55\u65b9\uff0c\u662f\u7531\u4ed6\u5468\u56f4\u7684\u670b\u53cb\u51b3\u5b9a\u7684\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"font-size: 15px;color: rgb(63, 63, 63);\">\u79ef\u6781\u7684\u4eba\u5c31\u50cf\u592a\u9633\uff0c\u7167\u5230\u54ea\u91cc\u54ea\u91cc\u4eae\u3002</span></p><p><br style=\"max-width: 100%;\"/></p><p style=\"line-height: 1.75em;letter-spacing: 0.5px;margin-left: 8px;margin-right: 8px;\"><span style=\"color: rgb(0, 0, 0);\"><strong><span style=\"font-size: 15px;\">\u613f\u6211\u4eec\u4e00\u76f4\u505a\u4e2a\u6b63\u80fd\u91cf\u7684\u4eba\uff0c\u6e29\u6696\u81ea\u5df1\uff0c\u4e5f\u6e29\u6696\u522b\u4eba\u3002</span></strong></span></p><p><br/></p></section>", "<p style=\"margin-right: 8px;margin-left: 8px;max-width: 100%;min-height: 1em;white-space: normal;outline: none;line-height: 1.75em;letter-spacing: 0.5px;text-align: center;box-sizing: border-box !important;word-wrap: break-word !important;\"><img class=\"\" data-backh=\"42\" data-backw=\"638\" data-before-oversubscription-url=\"http://zhugeleida.zhugeyingxiao.com/tianyan//statics/img/article_1554970282.3444529.jpg?\" data-ratio=\"0.065625\" src=\"http://zhugeleida.zhugeyingxiao.com/tianyan/statics/img/article_1554970282.3024478.jpg\" data-type=\"png\" data-w=\"640\" style=\"border-width: 0px;border-style: initial;border-color: initial;color: rgb(62, 62, 62);font-family: \u5fae\u8f6f\u96c5\u9ed1;font-size: 16px;letter-spacing: 0.544px;widows: 1;width: 100%;box-sizing: border-box !important;word-wrap: break-word !important;overflow-wrap: break-word !important;visibility: visible !important;height: auto;\" title=\"\u53f6\u5b50\u5206\u5272\u7ebf\" width=\"auto\"/></p>", "<p style=\"margin-right: 8px;margin-bottom: 5px;margin-left: 8px;max-width: 100%;min-height: 1em;letter-spacing: 0.544px;white-space: normal;outline: none;line-height: normal;box-sizing: border-box !important;overflow-wrap: break-word !important;text-align: justify;\"><span style=\"max-width: 100%;font-size: 12px;color: rgb(127, 127, 127);box-sizing: border-box !important;word-wrap: break-word !important;\">\u4f5c\u8005\uff1a\u516e\u516e\uff0c\u6765\u6e90\uff1a\u591c\u542c\u597d\u4e66\uff08ID\uff1aC9889C\uff09\uff0c\u4ece\u7ec6\u5fae\u4e4b\u5904\u611f\u53d7\u522b\u6837\u601d\u7ef4\uff0c\u4e00\u4e2a\u4e0d\u8d70\u5bfb\u5e38\u8def\u7684\u8350\u4e66\u591c\u542c\u3002\u4e00\u661f\u671f\u4e00\u672c\u4e66\u7ecf\u6388\u6743\u53d1\u5e03\u3002</span></p>", "<p style=\"margin-right: 8px;margin-bottom: 5px;margin-left: 8px;max-width: 100%;min-height: 1em;letter-spacing: 0.544px;white-space: normal;outline: none;line-height: normal;box-sizing: border-box !important;overflow-wrap: break-word !important;text-align: justify;\"><span style=\"max-width: 100%;font-size: 12px;color: rgb(127, 127, 127);box-sizing: border-box !important;word-wrap: break-word !important;\">\u4e3b\u64ad\uff1a\u4e9a\u6960\uff0c\u8d44\u6df1\u5a92\u4f53\u4eba\uff0c\u7f8e\u98df\u8fbe\u4eba\uff0c\u4e13\u6ce8\u5973\u6027\u6210\u957f\u548c\u513f\u7ae5\u6559\u80b2\u3002\u5fae\u4fe1\u53f7\uff1azhuboyanan23\u3002</span></p>", "<p style=\"margin-right: 8px;margin-bottom: 15px;margin-left: 8px;max-width: 100%;min-height: 1em;letter-spacing: 0.544px;white-space: normal;outline: none;line-height: normal;box-sizing: border-box !important;overflow-wrap: break-word !important;text-align: justify;\"><span style=\"max-width: 100%;font-size: 12px;color: rgb(127, 127, 127);box-sizing: border-box !important;word-wrap: break-word !important;\">\u7247\u5c3e\u66f2\uff1a\u8303\u73ae\u742a\u300a\u6084\u6084\u544a\u8bc9\u4f60\u300b</span></p>", "<p style=\"max-width: 100%;min-height: 1em;letter-spacing: 0.544px;white-space: normal;box-sizing: border-box !important;overflow-wrap: break-word !important;\"><img class=\"__bg_gif\" data-backh=\"372\" data-backw=\"654\" data-before-oversubscription-url=\"https://mmbiz.qpic.cn/mmbiz_gif/FqY4f41EBWe0Btnw3L70C4fh6n1ce0o5FPBtTRrzD0Vbic7icZjlGL8JjxcY0FWqax0gu0VzawZmAbR8Moh4mKfA/\" data-ratio=\"0.5694981\" src=\"http://zhugeleida.zhugeyingxiao.com/tianyan/statics/img/article_1554970282.309329.gif\" data-type=\"gif\" data-w=\"518\" style=\"border-width: 0px;border-style: initial;border-color: initial;letter-spacing: 0.544px;border-radius: 12px;width: 100%;box-sizing: border-box !important;word-wrap: break-word !important;overflow-wrap: break-word !important;visibility: visible !important;height: auto;\" width=\"100%\"/><img class=\"__bg_gif\" data-backh=\"73\" data-backw=\"558\" data-before-oversubscription-url=\"http://zhugeleida.zhugeyingxiao.com/tianyan//statics/img/article_1554970282.3570006.gif\" data-copyright=\"0\" data-ratio=\"0.13005780346820808\" src=\"http://zhugeleida.zhugeyingxiao.com/tianyan/statics/img/article_1554970282.3184288.gif\" data-type=\"gif\" data-w=\"692\" style=\"letter-spacing: 0.544px;text-align: right;border-width: 0px;border-style: initial;border-color: initial;box-sizing: border-box !important;overflow-wrap: break-word !important;visibility: visible !important;width: 677px !important;\"/></p>", "\n"]

for i in p:
    print(i)












