
import requests, random, time, os, re, json
from urllib.parse import unquote
from bs4 import BeautifulSoup
from publicFunc.base64_encryption import b64encode
from publicFunc.replace_chinese_character import replace_chinese_character
from publicFunc.qiniu_oper import update_qiniu, requests_img_download
from tianyanApi import settings

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
                sub_url = URL + file_dir
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
def get_article(article_url):
    headers = {'User-Agent': pcRequestHeader[random.randint(0, len(pcRequestHeader) - 1)]}
    ret = requests.get(article_url, headers=headers, timeout=5)
    ret.encoding = 'utf-8'
    s = requests.session()

    soup = BeautifulSoup(ret.text, 'lxml')
    title = re.compile(r'var msg_title = (.*);').findall(ret.text)[0].replace('"', '')  # 标题
    summary = re.compile(r'var msg_desc = (.*);').findall(ret.text)[0].replace('"', '')  # 摘要
    cover_url = re.compile(r'var msg_cdn_url = (.*);').findall(ret.text)[0].replace('"', '')  # 封面
    if summary:
        summary = replace_chinese_character(summary) # 替换中文符号

    ## 把封面图片下载到本地
    now_time = time.time()
    html = s.get(cover_url)
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
            html = s.get(data_src)

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
    iframe = body.find_all('iframe', attrs={'class': 'video_iframe'})
    for iframe_tag in iframe:
        print('----------------------------------获取到视频-------------------')
        shipin_url = iframe_tag.get('data-src')
        data_cover_url = iframe_tag.get('data-cover') # 封面
        if data_cover_url:
            data_cover_url = requests_img_download(data_cover_url) # 下载到本地
            data_cover_url = update_qiniu(data_cover_url)
            data_cover_url = unquote(data_cover_url, 'utf-8')

        iframe_url = 'https://mp.weixin.qq.com/mp/videoplayer?vid={}&action=get_mp_video_play_url'.format(
            shipin_url.split('vid=')[1]
        )
        ret = requests.get(iframe_url)
        try:
            # if len(ret.json().get('url_info')) >= 1:
            url = ret.json().get('url_info')[0].get('url')
            # else:
            #     if '&' in shipin_url and 'vid=' in shipin_url:
            #         vid_num = shipin_url.split('vid=')[1]
            #         _url = shipin_url.split('?')[0]
            #         shipin_url = _url + '?vid=' + vid_num
            #     url = shipin_url

            video_tag = """<div style="width: 100%; background: #000; position:relative; height: 0; padding-bottom:75%;">
                                       <video style="width: 100%; height: 100%; position:absolute;left:0;top:0;" id="videoBox" src="{}" poster="{}" controls="controls" allowfullscreen=""></video>
                                   </div>""".format(
                url,
                data_cover_url,
            )

            body = str(body).replace(str(iframe_tag), video_tag)
            body = BeautifulSoup(body, 'html.parser')
        except Exception as e:
            # if '&' in shipin_url and 'vid=' in shipin_url:
            #     vid_num = shipin_url.split('vid=')[1]
            #     _url = shipin_url.split('?')[0]
            #     shipin_url = _url + '?vid=' + vid_num

            iframe_tag.attrs['data-src'] = shipin_url
            iframe_tag.attrs['allowfullscreen'] = True      # 是否允许全屏
            iframe_tag.attrs['data-cover'] = data_cover_url


    # 生成css 文件
    now = time.time()
    style = style.replace('<style>', '').replace('</style>', '')
    style_path = os.path.join('statics', 'article_css') + '/{}.css'.format(now)
    with open(style_path, 'w') as e:
        e.write(style)
    # style_path = URL + '/statics/article_css/{}.css'.format(now)

    # 分布标签
    data_list = []
    for i in body:
        content = convert_content(s, str(i)) # 替换内容
        data_list.append(content)

    print('data_list----------------->', data_list)
    data = {
        'title': title,
        'summary':b64encode(summary),
        'cover_img':cover_url,
        'content': json.dumps(data_list),
        'style': style_path,
    }
    return data



if __name__ == '__main__':
    url = 'https://mp.weixin.qq.com/s/m5PqgqF7neEUJ_6ROeJQbQ'
    get_article(url)









