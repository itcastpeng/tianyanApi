import re
from publicFunc.forwarding_article import forwarding_article
from api import models


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













