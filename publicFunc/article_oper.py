from django.db.models import Q, F
from api import models
from django.http import JsonResponse
from publicFunc import Response
from publicFunc.base64_encryption import b64decode
import json
# 文章点赞增加/减少 数量
def give_like(article_id, customer_id=None, user_id=None):
    response = Response.ResponseObj()
    if customer_id:
        objs = models.SelectClickArticleLog.objects.filter(customer_id=customer_id, article_id=article_id)
    else:
        objs = models.SelectClickArticleLog.objects.filter(user_id=user_id, article_id=article_id)

    article_objs = models.Article.objects.filter(id=article_id)
    if objs:
        objs.delete()
        response.msg = '取消点赞'
        article_objs.update(  # 点赞次数減少
            like_num=F('like_num') - 1
        )
    else:
        if customer_id:
            models.SelectClickArticleLog.objects.create(**{
                'customer_id':customer_id,
                'article_id':article_id
            })
        else:
            models.SelectClickArticleLog.objects.create(**{
                'user_id': user_id,
                'article_id': article_id
            })
        response.msg = '点赞成功'

        article_objs.update(  # 点赞次数增加
            like_num=F('like_num') + 1
        )
    response.code = 200
    return response


# 创建文章
def add_article_public(data, classify_id=None):
    print('data--------------data-------创建文章-----》 ', data.get('create_user_id'),  data.get('title'), classify_id, type(classify_id))
    article_objs = models.Article.objects.filter(
        title=data.get('title'),
        create_user_id=data.get('create_user_id'),
        style=data.get('style')
    )
    if not article_objs:
        # if not classify_id:
        #     classify_id = 1  # 默认合众康桥
        print('-------***不存在 创建文章*****-----')
        obj = models.Article.objects.create(**data)
        if classify_id:
            if type(classify_id) == list:
                obj.classify = classify_id
            else:
                obj.classify = [classify_id]

            obj.save()
        id = obj.id
    else:
        print('-------***存在 返回文章*****-----')
        id = article_objs[0].id

    return id


# 获取用户 企业的 appid等信息
def get_ent_info(user_id, appid=None):
    print('---------# 获取用户 企业的 appid等信息-------------> ', user_id)
    if appid:
        ent_obj = models.Enterprise.objects.get(appid=appid)
        name = ''
        set_avator = ''
        openid = ''

    else:
        if not user_id:
            user_id = 1
        user_obj = models.Userprofile.objects.get(id=user_id)
        name = b64decode(user_obj.name)
        set_avator = user_obj.set_avator
        openid = user_obj.openid
        ent_obj = models.Enterprise.objects.get(id=user_obj.enterprise_id)

    data = {
        'id': ent_obj.id,
        'APPID': ent_obj.appid,
        'APPSECRET': ent_obj.appsecret,
        'access_token': ent_obj.access_token,
        'create_datetime': ent_obj.create_datetime,
        'user_name': name,
        'user_set_avator': set_avator,
        'openid': openid,
    }
    return data














