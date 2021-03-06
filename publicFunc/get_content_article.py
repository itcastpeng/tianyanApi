from urllib.parse import unquote, quote
from bs4 import BeautifulSoup
from publicFunc.base64_encryption import b64encode
from publicFunc.qiniu_oper import update_qiniu, requests_img_download
import requests, random, time, os, re, json, datetime



pcRequestHeader = [
    'Mozilla/5.0 (Windows NT 5.1; rv:6.0.2) Gecko/20100101 Firefox/6.0.2',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.52 Safari/537.17',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.16) Gecko/20101130 Firefox/3.5.16',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; .NET CLR 1.1.4322)',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2)',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
    'Mozilla/5.0 (Windows; U; Windows NT 5.2; zh-CN; rv:1.9.0.19) Gecko/2010031422 Firefox/3.0.19 (.NET CLR 3.5.30729)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.2)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.57 Safari/537.17',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13'
]

# URL = 'http://192.168.10.207:8008'
URL = 'http://zhugeleida.zhugeyingxiao.com/tianyan/'


# 替换内容
def convert_content(s, content):
    dict = {'url': '', 'data-src': 'src', '?wx_fmt=jpg': '', '?wx_fmt=png': '', '?wx_fmt=jpeg': '', '?wx_fmt=gif': ''}
    for key, value in dict.items():
        if key == 'url':
            pattern1 = re.compile(r'https:\/\/mmbiz.qpic.cn\/\w+\/\w+\/\w+\?\w+=\w+', re.I)  # 通过 re.compile 获得一个正则表达式对象
            pattern2 = re.compile(r'https:\/\/mmbiz.qpic.cn\/\w+\/\w+\/\w+', re.I)
            results_url_list_1 = pattern1.findall(content)
            results_url_list_2 = pattern2.findall(content)
            results_url_list_1.extend(results_url_list_2)
            for pattern_url in results_url_list_1:
                # print('pattern_url------> ', pattern_url)
                now_time = time.time()
                ## 把图片下载到本地
                html = s.get(pattern_url)
                if 'wx_fmt=gif' in pattern_url:
                    filename = "/article_%s.gif" % (now_time)
                else:
                    filename = "/article_%s.jpg" % (now_time)

                file_dir = os.path.join('statics', 'img') + filename
                with open(file_dir, 'wb') as file:
                    file.write(html.content)
                sub_url = update_qiniu(file_dir)
                # sub_url = URL + file_dir
                # sub_url = URL + '/statics/img' + filename
                content = content.replace(pattern_url, sub_url)
        else:
            content = content.replace(key, value)
    return content

# 剔除A标签
def eliminate_label(i):
    flag = False
    soup = BeautifulSoup(str(i), 'lxml')
    if soup.find_all('a'):
        flag = True
    return flag



# 放入微信文章 获取全部内容
def get_article(article_url, get_content=None):
    headers = {'User-Agent': pcRequestHeader[random.randint(0, len(pcRequestHeader) - 1)]}
    ret = requests.get(article_url, headers=headers, timeout=10, verify=False)
    ret.encoding = 'utf-8'
    s = requests.session()
    is_video_original_link = None # 是否有视频 如果有则返回原文链接
    soup = BeautifulSoup(ret.text, 'lxml')

    if not get_content:
        title = re.compile(r'var msg_title = (.*);').findall(ret.text)[0].replace('"', '')  # 标题
        summary = re.compile(r'var msg_desc = (.*);').findall(ret.text)[0].replace('"', '')  # 摘要
        cover_url = re.compile(r'var msg_cdn_url = (.*);').findall(ret.text)[0].replace('"', '')  # 封面

        ## 把封面图片下载到本地
        now_time = time.time()
        # print('--------------------请求封面-0-----------> ', datetime.datetime.today(), cover_url)
        html = s.get(cover_url)
        # print('--------------------结束请求封面-0-----------> ', datetime.datetime.today())
        if 'wx_fmt=gif' in cover_url:
            cover_name = "/cover_%s.gif" % (now_time)
        else:
            cover_name = "/cover_%s.jpg" % (now_time)
        cover_url = os.path.join('statics', 'img') + cover_name
        with open(cover_url, 'wb') as file:
            file.write(html.content)
        cover_url = update_qiniu(cover_url)

    # 获取所有样式
    style = ""
    style_tags = soup.find_all('style')
    for style_tag in style_tags:
        style += str(style_tag)

    # 获取所有图片
    body = soup.find('div', id="js_content")
    body.attrs['style'] = "padding: 20px 16px 12px;"
    img_tags = soup.find_all('img')
    for img_tag in img_tags:
        data_src = img_tag.attrs.get('data-src')
        if data_src:
            if img_tag.attrs.get('style'):
                img_tag.attrs['style'] = img_tag.attrs.get('style')

            now_time = time.time()
            # print('------------------开始请求图片----------->', datetime.datetime.today(), data_src)
            html = s.get(data_src)
            # print('------------------结束请求图片----------->', datetime.datetime.today())

            if 'wx_fmt=gif' in data_src:
                img_name = "/article_%s.gif" % (now_time)
            else:
                img_name = "/article_%s.jpg" % (now_time)

            file_dir = os.path.join('statics', 'img') + img_name
            with open(file_dir, 'wb') as file:
                file.write(html.content)
            img_url = update_qiniu(file_dir)
            img_tag.attrs['data-src'] = img_url
            #  img_tag.attrs['data-src'] = URL + '/statics/img' + img_name

    ## 处理视频的URL
    flag = False # 判断是否有 视频
    iframe = body.find_all('iframe', attrs={'class': 'video_iframe'})
    for iframe_tag in iframe:
        shipin_url = iframe_tag.get('data-src')
        data_cover_url = iframe_tag.get('data-cover') # 封面
        if data_cover_url:
            data_cover_url = unquote(data_cover_url, 'utf-8')
        data_cover_url = requests_img_download(data_cover_url) # 下载到本地
        data_cover_url = update_qiniu(data_cover_url)
        vid = shipin_url.split('vid=')[1]
        if 'wxv' in vid:  # 下载
            flag = True
            iframe_url = 'https://mp.weixin.qq.com/mp/videoplayer?vid={}&action=get_mp_video_play_url'.format(vid)
            ret = requests.get(iframe_url)
            video_path = ret.json().get('url_info')[0].get('url')
            iframe_tag_new = """<div style="width: 100%; background: #000; position:relative; height: 0; padding-bottom:75%;">
                                       <video style="width: 100%; height: 100%; position:absolute;left:0;top:0;" id="videoBox" src="{}" poster="{}" controls="controls" allowfullscreen=""></video>
                                   </div>""".format(video_path, data_cover_url)

        else:
            shipin_url = 'https://v.qq.com/txp/iframe/player.html?origin=https%3A%2F%2Fmp.weixin.qq.com&vid={}&autoplay=false&full=true&show1080p=false&isDebugIframe=false'.format(
                vid
            )
            iframe_tag.attrs['data-src'] = shipin_url
            iframe_tag.attrs['allowfullscreen'] = True  # 是否允许全屏
            iframe_tag.attrs['data-cover'] = data_cover_url

            iframe_tag_new = str(iframe_tag).replace('></iframe>', ' width="100%" height="300px"></iframe>')


        body = str(body).replace(str(iframe_tag), iframe_tag_new)
        body = BeautifulSoup(body, 'html.parser')

    content = str(style) + str(body)
    content = BeautifulSoup(content, 'html.parser')
    if not get_content:
        # 生成css 文件
        now = time.time()
        style = style.replace('<style>', '').replace('</style>', '')
        style_path = os.path.join('statics', 'article_css') + '/{}.css'.format(now)
        with open(style_path, 'w') as e:
            e.write(style)
        # style_path = URL + '/statics/article_css/{}.css'.format(now)

    # 分布标签
    data_list = []
    for i in content:
        content = convert_content(s, str(i)) # 替换内容
        data_list.append(content)

    if flag:
        is_video_original_link = article_url # 原文链接

    if not get_content:
        data = {
            'title': title,
            'summary':b64encode(summary),
            'cover_img':cover_url,
            'content': json.dumps(data_list),
            'style': style_path,
            'original_link': is_video_original_link,
        }
    else:
        data = {
            'content': json.dumps(data_list),
        }
    return data



if __name__ == '__main__':
    url = 'https://mp.weixin.qq.com/s/m5PqgqF7neEUJ_6ROeJQbQ'
    get_article(url)









