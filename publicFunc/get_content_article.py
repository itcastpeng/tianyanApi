


import requests, random, time, os, re
from urllib.parse import unquote
from bs4 import BeautifulSoup


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



# 发送文章链接获取内容
def get_content_article(article_url):
    headers = {'User-Agent': pcRequestHeader[random.randint(0, len(pcRequestHeader) - 1)]}
    ret = requests.get(article_url, headers=headers, timeout=5)
    soup = BeautifulSoup(ret.text, 'lxml')
    title = soup.find('title').get_text().strip() # 获取标题

    js_content_tag = soup.find(id='js_content')
    p_all_tags = js_content_tag.find_all('p')
    data_list = []

    for p_all_tag in p_all_tags:
        print('p_all_tag-----> ', p_all_tag)
        # text = p_all_tag.get_text()

        # if p_all_tag.find('img'):
        #     text = p_all_tag.find('img').attrs.get('data-src')
        p_all_tag = str(p_all_tag).replace('data-src', 'src').replace('?wx_fmt=png', '').replace('?wx_fmt=gif', '')
        data_list.append(p_all_tag)

    data_dict = {
        'title': title,
        'data_list': data_list
    }
    return data_dict

# URL = 'http://127.0.0.1:8001'
URL = 'http://zhugeleida.zhugeyingxiao.com/tianyan/'


def get_article(article_url):
    headers = {'User-Agent': pcRequestHeader[random.randint(0, len(pcRequestHeader) - 1)]}
    ret = requests.get(article_url, headers=headers, timeout=5)
    ret.encoding = 'utf8'
    soup = BeautifulSoup(ret.text, 'lxml')

    title = re.compile(r'var msg_title = (.*);').findall(ret.text)[0].replace('"', '')  # 标题
    summary = re.compile(r'var msg_desc = (.*);').findall(ret.text)[0].replace('"', '')  # 摘要
    cover_url = re.compile(r'var msg_cdn_url = (.*);').findall(ret.text)[0].replace('"', '')  # 封面

    s = requests.session()
    ## 把封面图片下载到本地
    now_time = int(time.time())
    html = s.get(cover_url)
    if 'wx_fmt=gif' in cover_url:
        cover_name = "/cover_%s.gif" % (now_time)
    else:
        cover_name = "/cover_%s.jpg" % (now_time)

    cover_url = os.path.join('statics', 'img') + cover_name
    with open(cover_url, 'wb') as file:
        file.write(html.content)

    # 获取所有样式
    style = ""
    style_tags = soup.find_all('style')
    for style_tag in style_tags:
        print('style_tag -->', style_tag)
        style += str(style_tag)

    # 获取内容
    body = soup.find('div', id="js_content")
    body.attrs['style'] = "padding: 20px 16px 12px;"
    img_tags = soup.find_all('img')
    for img_tag in img_tags:
        data_src = img_tag.attrs.get('data-src')
        if data_src:

            now_time = int(time.time())
            html = s.get(data_src)

            if 'wx_fmt=gif' in data_src:
                img_name = "/article_%s.gif" % (now_time)
            else:
                img_name = "/article_%s.jpg" % (now_time)

            file_dir = os.path.join('statics', 'img') + img_name
            with open(file_dir, 'wb') as file:
                file.write(html.content)
            img_tag.attrs['data-src'] = URL + file_dir

    ### 处理视频的URL
    iframe = body.find_all('iframe', attrs={'class': 'video_iframe'})

    for iframe_tag in iframe:
        shipin_url = iframe_tag.get('data-src')
        data_cover_url = iframe_tag.get('data-cover')
        if data_cover_url:
            data_cover_url = unquote(data_cover_url, 'utf-8')

        print('封面URL data_cover_url ------->>', data_cover_url)

        if '&' in shipin_url and 'vid=' in shipin_url:
            vid_num = shipin_url.split('vid=')[1]
            _url = shipin_url.split('?')[0]
            shipin_url = _url + '?vid=' + vid_num

        iframe_tag.attrs['data-src'] = shipin_url
        iframe_tag.attrs['allowfullscreen'] = True
        iframe_tag.attrs['data-cover'] = data_cover_url

    content = str(style) + str(body)

    dict = {'url': '', 'data-src': 'src', '?wx_fmt=jpg': '', '?wx_fmt=png': '', '?wx_fmt=jpeg': '', '?wx_fmt=gif': '', }
    for key, value in dict.items():
        if key == 'url':
            pattern1 = re.compile(r'https:\/\/mmbiz.qpic.cn\/\w+\/\w+\/\w+\?\w+=\w+', re.I)  # 通过 re.compile 获得一个正则表达式对象
            pattern2 = re.compile(r'https:\/\/mmbiz.qpic.cn\/\w+\/\w+\/\w+', re.I)
            results_url_list_1 = pattern1.findall(content)
            results_url_list_2 = pattern2.findall(content)
            # print(' 匹配的微信图片链接 results_url_list_1 ---->', json.dumps(results_url_list_1))
            # print(' 匹配的微信图片链接 results_url_list_2 ---->', json.dumps(results_url_list_2))
            results_url_list_1.extend(results_url_list_2)

            for pattern_url in results_url_list_1:
                now_time = int(time.time())
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
                content = content.replace(pattern_url, sub_url)

        else:
            content = content.replace(key, value)
    print('title-------> ', title)
    print('summary------> ', summary)
    print('cover_url------> ', cover_url)
    print('content------> ', content)
    return title, summary, cover_url, content













