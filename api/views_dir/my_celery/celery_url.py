from api import models
from publicFunc import Response
from django.http import JsonResponse
from django.db.models import Count
from publicFunc.base64_encryption import b64decode, b64encode
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
from publicFunc.article_oper import get_ent_info
import datetime, json, time








# 创建天眼公众号 导航栏
def create_menu(request):
    response = Response.ResponseObj()
    data = get_ent_info(1)
    weixin_objs = WeChatApi(data)
    APPID = weixin_objs.APPID
    weixin_objs.getMenu() # 获取自定义菜单栏列表


    redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/user_login/user_login_get_info'
    login_url = "https://open.weixin.qq.com/connect/oauth2/authorize?" \
                 "appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo" \
                 "&state=STATE#wechat_redirect" \
        .format(
        appid=APPID,
        redirect_uri=redirect_uri,
    )
    redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/user_login/huoke'
    huoke_url = "https://open.weixin.qq.com/connect/oauth2/authorize?" \
                "appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo" \
                "&state=STATE#wechat_redirect" \
        .format(
        appid=APPID,
        redirect_uri=redirect_uri,
    )
    redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/user_login/wodepinpai'
    pinpai_url = "https://open.weixin.qq.com/connect/oauth2/authorize?" \
                "appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo" \
                "&state=STATE#wechat_redirect" \
        .format(
        appid=APPID,
        redirect_uri=redirect_uri,
    )
    redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/user_login/wodedianpu'
    dianpu_url = "https://open.weixin.qq.com/connect/oauth2/authorize?" \
                "appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo" \
                "&state=STATE#wechat_redirect" \
        .format(
        appid=APPID,
        redirect_uri=redirect_uri,
    )
    redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/user_login/tuiguang'
    tuiguang_url = "https://open.weixin.qq.com/connect/oauth2/authorize?" \
                 "appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo" \
                 "&state=STATE#wechat_redirect" \
        .format(
        appid=APPID,
        redirect_uri=redirect_uri,
    )
    button = {
        "button": [
            {
                "name": "获客文章",
                "sub_button": [
                    {
                        "type": "view",
                        "name": "文章首页",
                        "url": huoke_url
                    },
                    {
                        "type": "view",
                        "name": "我的品牌",
                        "url": pinpai_url,
                    },
                    {
                        "type": "view",
                        "name": "我的店铺",
                        "url": dianpu_url,
                    }]
            },
            {
                "type": "view",
                "name": "天眼",
                "url": login_url,
            },
            {
                "name": "设置",
                "sub_button": [
                    {
                        "type": "view",
                        "name": "我的名片",
                        "url": login_url
                    },
                    {
                        "type": "view",
                        "name": "我的分销",
                        "url": tuiguang_url,
                    },
                    {
                        "type": "view",
                        "name": "使用指南",
                        "url": login_url,
                    }]
            },
        ]
    }
    print('button-button---button--------> ', button)
    # weixin_objs.createMenu(button)


    response.code = 200

    return JsonResponse(response.__dict__)





# 天眼功能统计数据
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
                user_id=user_id,
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



# 最后活跃时间马上到24小时的 发送模板消息
def last_active_time(request):
    response = Response.ResponseObj()
    return JsonResponse(response.__dict__)







