
# from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.day_eye import SelectForm, AddForm, UpdateForm
from django.db.models import Count
from publicFunc.base64_encryption import b64decode, b64encode
import json
import datetime


def day_eye_data(request):
    response = Response.ResponseObj()
    for i in models.Userprofile.objects.all():
        user_id = i.id
        objs = models.SelectArticleLog.objects.filter(
            inviter_id=user_id
        ).select_related(
            'customer'
        ).values(
            'customer_id', 'customer__name', 'customer__set_avator'
        ).annotate(Count('customer_id')).exclude(customer_id__isnull=True).distinct()

        # 返回的数据
        data_list = []
        for obj in objs:
            customer_id = obj.get('customer_id')
            customer__name = ''
            if obj.get('customer__name'):
                customer__name = b64decode(obj.get('customer__name'))

            article_objs = models.SelectArticleLog.objects.filter(
                customer_id=customer_id,
                inviter_id=user_id,
            ).distinct().order_by('-create_datetime')

            article_count = article_objs.count()
            data_list.append({
                'customer_id': customer_id,
                'customer__name': customer__name,
                'customer__set_avator': obj.get('customer__set_avator'),

                'text': '看了{}篇文章, 总共查看{}次'.format(
                    article_count,  # 总共查看几篇文章
                    obj.get('customer_id__count')  # # 总共查看几次
                ),
                'status': 1,  # 代表文章
                'create_date': article_objs[0].create_datetime.strftime('%Y-%m-%d %H:%M:%S')  # 代表文章
            })

        objs = models.customer_look_goods_log.objects.filter(
            user_id=user_id
        ).select_related(
            'customer'
        ).values(
            'customer_id', 'customer__name', 'customer__set_avator'
        ).annotate(Count('customer_id')).exclude(customer_id__isnull=True).distinct()
        for obj in objs:
            customer_id = obj.get('customer_id')
            customer__name = ''
            if obj.get('customer__name'):
                customer__name = b64decode(obj.get('customer__name'))

            goods_objs = models.customer_look_goods_log.objects.filter(
                customer_id=customer_id,
                user_id=user_id,
            ).distinct().order_by('-create_datetime')
            goods_count = goods_objs.count()
            data_list.append({
                'customer_id': customer_id,
                'customer__name': customer__name,
                'customer__set_avator': obj.get('customer__set_avator'),

                'text': '看了{}件商品, 总共查看{}次'.format(
                    goods_count,  # 总共查看几篇文章
                    obj.get('customer_id__count')  # # 总共查看几次
                ),
                'status': 2,  # 代表商品
                'create_date': goods_objs[0].create_datetime.strftime('%Y-%m-%d %H:%M:%S')  # 代表文章
            })
        for i in data_list:
            eye_objs = models.day_eye_celery.objects.filter(
                user_id=i.get('user_id'),
                status=i.get('status'),
                customer_id=i.get('customer_id'),
            )
            if eye_objs:
                eye_objs.update(
                    text = i.get('text'),
                    create_date = i.get('create_date'),
                )
            else:
                models.day_eye_celery.objects.create(
                    user_id=user_id,
                    status=i.get('status'),
                    customer_id=i.get('customer_id'),
                    text=i.get('text'),
                    create_date=i.get('create_date'),
                )

    response.code = 200
    return JsonResponse(response.__dict__)











