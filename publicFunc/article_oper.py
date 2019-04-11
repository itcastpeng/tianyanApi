from django.db.models import Q, F
from api import models
from django.http import JsonResponse
from publicFunc import Response


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
    print('data--------------data-------创建文章-----》 ', data)
    article_objs = models.Article.objects.filter(
        title=data.get('title'),
        create_user_id=data.get('usercreate_user_id_id'),
        style=data.get('style')
    )
    if not article_objs:
        print('-------***不存在 创建文章*****-----')
        obj = models.Article.objects.create(**data)
        if classify_id:
            obj.classify = classify_id
            obj.save()
        id = obj.id
    else:
        print('-------***存在 返回文章*****-----')
        id = article_objs[0].id

    return id



















