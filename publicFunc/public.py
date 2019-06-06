from publicFunc.forwarding_article import forwarding_article
from api import models
from PIL import Image, ImageFont, ImageDraw
from publicFunc.article_oper import get_ent_info
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
from publicFunc.account import randon_str
import re, datetime, requests, os, sys

# 验证手机号
def verify_mobile_phone_number(phone):
    flag = False
    phone_pat = re.compile('^(13\d|14[5|7]|15\d|166|17[3|6|7]|18\d)\d{8}$')
    res = re.search(phone_pat, phone)
    if res:
        flag = True

    return flag

# 随机查询 该用户三篇文章
def randomly_query_three_articles(user_id, id=None):
    article_objs = models.Article.objects.filter(
        title__isnull=False,
        create_user_id=user_id
    ).exclude(
        id=id
    ).order_by('-look_num')[:3]

    popula_articles_list = []
    for article_obj in article_objs:
        pub = 'article_' + str(article_obj.id)
        url = forwarding_article(
            pub=pub,
            user_id=user_id,
        )
        popula_articles_list.append({
            'title': article_obj.title,
            'cover_img':article_obj.cover_img + '?imageView2/2/w/200',
            'url':url
        })

    return popula_articles_list

# 查询商品
def get_hot_commodity(user_id):
    goods_list = []
    good_objs = models.Goods.objects.filter(goods_classify__oper_user_id=user_id)

    good_count = good_objs.count()
    if good_count >= 2:
        good_objs = good_objs[0:2]
    elif good_count <= 0:
        good_objs = good_objs
    else:
        good_objs = good_objs[0:1]

    for good_obj in good_objs:
        pub = 'micro_' + str(good_obj.id)
        url = forwarding_article(
            pub=pub,
            user_id=good_obj.goods_classify.oper_user_id,
        )
        goods_list.append({
            'price': good_obj.price,  # 商品价格
            'goods_name': good_obj.goods_name,  # 商品名称
            'cover_img': good_obj.cover_img + '?imageView2/2/w/200',  # 封面图
            'url': url
        })
    return goods_list

# 续费 时长计算
def length_the_days(the_length):
    if int(the_length) == 1:  # 三个月
        renewal_number_days = 90
    elif int(the_length) == 2: # 一年
        renewal_number_days = 365
    else:  # 三年
        renewal_number_days = 1095

    return the_length, renewal_number_days

# 记录 用户和公众号互动 日志 (某个客户什么时间做了什么)
def pub_log_access(user_id, msg):
    models.log_access.objects.create(
        oper_user_id=user_id,
        message=msg,
    )


# 生成圆图
def circle(img, path):
    ima = Image.open(img).convert("RGBA")
    size = ima.size

    # 因为是要圆形，所以需要正方形的图片
    r2 = min(size[0], size[1])
    if size[0] != size[1]:
        ima = ima.resize((r2, r2), Image.ANTIALIAS)

    # 最后生成圆的半径
    r3 = 60
    imb = Image.new('RGBA', (r3 * 2, r3 * 2), (26, 172, 25))
    pima = ima.load()  # 像素的访问对象
    pimb = imb.load()
    r = float(r2 / 2)  # 圆心横坐标

    for i in range(r2):
        for j in range(r2):
            lx = abs(i - r)  # 到圆心距离的横坐标
            ly = abs(j - r)  # 到圆心距离的纵坐标
            l = (pow(lx, 2) + pow(ly, 2)) ** 0.5  # 三角函数 半径

            if l < r3:
                pimb[i - (r - r3), j - (r - r3)] = pima[i, j]
    imb.save(path)

# 生成推广二维码
def tuiguang(user_id):
    # 获取用户数据
    data = get_ent_info(user_id)
    weichat_api_obj = WeChatApi(data)
    print('-----------------开始生成二维码=-==========================', datetime.datetime.today())
    qc_code_url = weichat_api_obj.generate_qrcode({'inviter_user_id': user_id}) # 生成二维码
    print('-----------------结束生成二维码=-==========================', datetime.datetime.today())
    expire_date = (datetime.datetime.now().date() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    name = data.get('user_name') # 用户名
    user_set_avator = data.get('user_set_avator') # 用户头像

    img_path = os.path.join('statics', 'img', randon_str() + '.png') # 推广二维码图片 保存位置

    # 下载二维码
    linshi_qc_code_url_path = os.path.join('statics', 'img', randon_str() + '.png')
    ret = requests.get(qc_code_url)
    with open(linshi_qc_code_url_path, 'wb') as f:
        f.write(ret.content)

    # 下载头像
    old_linshi_user_set_avator_path = os.path.join('statics', 'img', randon_str() + '.png')
    ret = requests.get(user_set_avator)
    with open(old_linshi_user_set_avator_path, 'wb') as f:
        f.write(ret.content)

    new_linshi_user_set_avator_path = os.path.join('statics', 'img', randon_str() + '.png') # 圆形头像 保存位置

    huabu_x = 375  # 画布宽度
    huabu_y = 550  # 画布高度
    title1 = '我正在使用 微商天眼 进行'
    title2 = '客户追踪、分 享 事 业 机 会'
    title3 = '伙伴们一起来吧 !'
    title4 = '客 户 追 踪 神 器'
    title5 = '关注微商天眼公众号'

    # 新建画布纯白色           宽度↓   ↓高度    ↓ 颜色
    p = Image.new('RGBA', (huabu_x, huabu_y), (26, 172, 25))
    image_draw = ImageDraw.Draw(p)
    if 'linux' in sys.platform:  # 获取平台
        font = ImageFont.truetype('/usr/share/fonts/chinese/MSYHL.TTC', 18)
        font1 = ImageFont.truetype('/usr/share/fonts/chinese/MSYHBD.TTC', 18)
        font2 = ImageFont.truetype('/usr/share/fonts/chinese/MSYHL.TTC', 12)
        font3 = ImageFont.truetype('/usr/share/fonts/chinese/MSYHL.TTC', 15)
    else:
        font = ImageFont.truetype('/usr/share/fonts/chinese/msyhl.ttc', 18)
        font1 = ImageFont.truetype('/usr/share/fonts/chinese/msyhbd.ttc', 18)
        font2 = ImageFont.truetype('/usr/share/fonts/chinese/msyhl.ttc', 12)
        font3 = ImageFont.truetype('/usr/share/fonts/chinese/msyhl.ttc', 15)

    circle(old_linshi_user_set_avator_path, new_linshi_user_set_avator_path)
    touxiang_img = Image.open(new_linshi_user_set_avator_path)
    touxiang_img = touxiang_img.resize((70, 70))
    p.paste(touxiang_img, (int((huabu_x - 50) / 2), 30))
    name_x, name_y = image_draw.textsize(name, font=font)
    image_draw.text((int((huabu_x - name_x) / 2) + 10, 100), name, font=font3, fill=(248, 248, 242))

    # 二维码
    erweima_img = Image.open(linshi_qc_code_url_path)
    erweima_img = erweima_img.resize((100, 100))
    p.paste(erweima_img, (huabu_x - 130, huabu_y - 130))

    # logo
    logo_path = os.path.join('statics', 'img', 'promote_eye.png')
    logo_img = Image.open(logo_path)
    logo_img = logo_img.resize((100, 100))
    p.paste(logo_img, (int((huabu_x - 100) / 2), int((huabu_y - 100) / 2)))

    # 左1线(粗线)
    image_draw.line(((5, 5), (5, huabu_y - 5)), fill=(248, 248, 242), width=2)
    # 左2线(细线)
    image_draw.line(((13, 12), (13, huabu_y - 13)), fill=(248, 248, 242), width=1)
    # 上1线
    image_draw.line(((5, 5), (huabu_x - 5, 5)), fill=(248, 248, 242), width=2)
    # 上2线
    image_draw.line(((13, 12), (huabu_x - 13, 12)), fill=(248, 248, 242), width=1)
    # 右1线
    image_draw.line(((huabu_x - 5, 5), (huabu_x - 5, huabu_y - 5)), fill=(248, 248, 242), width=2)
    # 右2线
    image_draw.line(((huabu_x - 13, 12), (huabu_x - 13, huabu_y - 12)), fill=(248, 248, 242), width=1)
    # 下1线
    image_draw.line(((5, huabu_y - 5), (huabu_x - 5, huabu_y - 5)), fill=(248, 248, 242), width=2)
    # 下2线
    image_draw.line(((13, huabu_y - 12), (huabu_x - 13, huabu_y - 12)), fill=(248, 248, 242), width=1)

    title1_x, title1_y = image_draw.textsize(title1, font=font)
    title2_x, title2_y = image_draw.textsize(title2, font=font)
    title4_x, title4_y = image_draw.textsize(title4, font=font)

    touxiangweizhi = 130  # 头像预留大小
    ziti_x = (huabu_x - title1_x) / 2  # 字体左侧位置

    image_draw.text((ziti_x, touxiangweizhi), title1, font=font, fill=(248, 248, 242))
    image_draw.text((ziti_x, touxiangweizhi + title1_y + 5), title2, font=font1, fill=(248, 248, 242))
    image_draw.text((ziti_x, touxiangweizhi + title1_y + title2_y + 15), title3, font=font, fill=(248, 248, 242))
    image_draw.text((25, huabu_y - 130), title4, font=font1, fill=(248, 248, 242))
    image_draw.text((25, (huabu_y - 130) + title4_y), title5, font=font2, fill=(248, 248, 242))

    # 画箭头
    image_draw.line(((50 + title4_x, huabu_y - 130 + title4_y), (70 + title4_x, huabu_y - 130 + title4_y)),
        fill=(248, 248, 242), width=10)
    image_draw.line(((65 + title4_x, huabu_y - 140 + title4_y), (65 + title4_x, huabu_y - 120 + title4_y)),
        fill=(248, 248, 242), width=1)  # 竖线

    image_draw.line(((65 + title4_x, huabu_y - 140 + title4_y), (70 + title4_x + 5, huabu_y - 130 + title4_y)),
        fill=(248, 248, 242), width=1)
    image_draw.line(((65 + title4_x, huabu_y - 120 + title4_y), (70 + title4_x + 5, huabu_y - 130 + title4_y)),
        fill=(248, 248, 242), width=1)

    num_x = 65
    num_y1 = 140
    num_y2 = 120
    for i in range(10):
        image_draw.line(
            ((num_x + title4_x, huabu_y - num_y1 + title4_y), (num_x + title4_x, huabu_y - num_y2 + title4_y)),
            fill=(248, 248, 242), width=1)
        num_x += 1
        num_y1 -= 1
        num_y2 += 1

    p.save(img_path)
    os.remove(old_linshi_user_set_avator_path)
    os.remove(linshi_qc_code_url_path)          # 删除下载的二维码
    os.remove(new_linshi_user_set_avator_path)
    return img_path, expire_date







