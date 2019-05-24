from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.base64_encryption import b64decode
import requests, datetime, random, json



# token验证 我的名片
@account.is_token(models.Userprofile)
def my_business_card(request):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')

    if request.method == "GET":
        obj = models.Userprofile.objects.get(id=user_id)
        name = b64decode(obj.name)
        if not obj.introduction:
            introduction = '我是{}, 热烈欢迎来到我的名片'.format(name)
        else:
            introduction = obj.introduction

        article_list = []
        article_objs = models.Article.objects.filter(create_user_id=user_id).order_by('-create_datetime')
        article_count = article_objs.count()
        if article_count > 3:
            article_objs = article_objs[: 3]
        for article_obj in article_objs:
            article_list.append({
                'article_id': article_obj.id,
                'title': article_obj.title,
                'cover_img': article_obj.cover_img + '?imageView2/2/w/200',
            })


        goods_list = []
        goods_objs = models.Goods.objects.filter(goods_classify__oper_user_id=user_id).order_by('-create_datetime')
        goods_objs_count = goods_objs.count()
        if goods_objs_count > 3:
            goods_objs = goods_objs[:3]
        for goods_obj in goods_objs:
            goods_list.append({
                'goods_id': goods_obj.id,
                'cover_img': goods_obj.cover_img + '?imageView2/2/w/200',
                'goods_name': goods_obj.goods_name,
            })


        data_list = {
            'user_id': obj.id,
            'introduction':introduction,
            'user_name': name,
            'set_avator': obj.set_avator + '?imageView2/2/w/100',
            'article_list': article_list,
            'goods_list': goods_list,
        }

        response.code = 200
        response.msg = '查询成功'
        response.data = data_list

    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)


@account.is_token(models.Userprofile)
def my_business_card_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')

    if request.method == 'POST':

        # 修改 名片简介
        if oper_type == 'update_introduction':
            introduction = request.POST.get('introduction')
            models.Userprofile.objects.filter(id=user_id).update(introduction=introduction)
            response.code = 200
            response.msg = '修改成功'

    else:
        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)

































