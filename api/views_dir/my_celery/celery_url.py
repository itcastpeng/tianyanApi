from api import models
from publicFunc import Response
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from publicFunc.base64_encryption import b64decode, b64encode
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
from publicFunc.article_oper import get_ent_info
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
from publicFunc import base64_encryption
import datetime, json, time, requests

# 报错警告  celery捕获异常 发送客服消息 到管理员
def celery_error_warning(msg):
    print('*********!!!!!!!!!!!!!!!!!!!!!!!!!!!!!******************!!!!!!!!!!!!!!!!!!!!!!*************!!!!!!!!!!', msg)
    user_info = get_ent_info(1)
    weixin_objs = WeChatApi(user_info)

    openid_list = [
        'oX0xv1iqlzEtIhkeutd6f_wzAEpM', # 赵欣鹏
        'oX0xv1pmPrR24l6ezv4mI9HE0-ME', # 小明
    ]
    for i in openid_list:
        post_data = {
            "touser": i,
            "msgtype": "text",
            "text": {
                "content": msg
            }
        }

        # 发送客服消息
        post_data = bytes(json.dumps(post_data, ensure_ascii=False), encoding='utf-8')
        weixin_objs.news_service(post_data)

# 创建天眼公众号 导航栏
def create_menu(request):
    response = Response.ResponseObj()
    data = get_ent_info(1)
    weixin_objs = WeChatApi(data)
    APPID = weixin_objs.APPID
    # weixin_objs.getMenu() # 获取自定义菜单栏列表


    redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/user_login/user_login_get_info'
    login_url = "https://open.weixin.qq.com/connect/oauth2/authorize?" \
                 "appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo" \
                 "&state=STATE#wechat_redirect&connect_redirect=1" \
        .format(
        appid=APPID,
        redirect_uri=redirect_uri,
    )
    redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/user_login/wodepinpai'
    pinpai_url = "https://open.weixin.qq.com/connect/oauth2/authorize?" \
                "appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo" \
                "&state=STATE#wechat_redirect&connect_redirect=1" \
        .format(
        appid=APPID,
        redirect_uri=redirect_uri,
    )
    redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/user_login/wodedianpu'
    dianpu_url = "https://open.weixin.qq.com/connect/oauth2/authorize?" \
                "appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo" \
                "&state=STATE#wechat_redirect&connect_redirect=1" \
        .format(
        appid=APPID,
        redirect_uri=redirect_uri,
    )
    redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/user_login/tuiguang'
    tuiguang_url = "https://open.weixin.qq.com/connect/oauth2/authorize?" \
                 "appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo" \
                 "&state=STATE#wechat_redirect&connect_redirect=1" \
        .format(
        appid=APPID,
        redirect_uri=redirect_uri,
    )
    redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/user_login/tianyan'
    tianyan_url = "https://open.weixin.qq.com/connect/oauth2/authorize?" \
                   "appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo" \
                   "&state=STATE#wechat_redirect&connect_redirect=1" \
        .format(
        appid=APPID,
        redirect_uri=redirect_uri,
    )
    redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/user_login/shezhi'
    shezhi_url = "https://open.weixin.qq.com/connect/oauth2/authorize?" \
                  "appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo" \
                  "&state=STATE#wechat_redirect&connect_redirect=1" \
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
                        "name": "获客文章",
                        "url": login_url
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
                "url": tianyan_url,
            },
            {
                "name": "我的",
                "sub_button": [
                    {
                        "type": "view",
                        "name": "设置",
                        "url": shezhi_url
                    },
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
    try:
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
                )


                article_count = article_objs.values(
                    'customer_id',
                    'article_id',
                    'inviter_id'
                ).distinct().count()

                data_list.append({
                    'customer_id': customer_id,
                    'customer__name': customer__name,
                    'customer__set_avator': obj.get('customer__set_avator'),

                    'text': '看了{}篇文章, 总共查看{}次'.format(
                        article_count,  # 总共查看几篇文章
                        obj.get('customer_id__count')  # # 总共查看几次
                    ),
                    'status': 1,  # 代表文章
                    'create_date': article_objs.order_by('-create_datetime')[0].create_datetime.strftime('%Y-%m-%d %H:%M:%S')  # 代表文章
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
                )
                goods_count = goods_objs.values(
                    'customer_id',
                    'goods_id',
                    'user_id',
                ).distinct().count()
                data_list.append({
                    'customer_id': customer_id,
                    'customer__name': customer__name,
                    'customer__set_avator': obj.get('customer__set_avator'),

                    'text': '看了{}件商品, 总共查看{}次'.format(
                        goods_count,  # 总共查看几篇文章
                        obj.get('customer_id__count')  # # 总共查看几次
                    ),
                    'status': 2,  # 代表商品
                    'create_date': goods_objs.order_by('-create_datetime')[0].create_datetime.strftime('%Y-%m-%d %H:%M:%S')  # 代表文章
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
    except Exception as e:
        msg = '警告:{}, \n错误:{}, \n时间:{}'.format(
            'celery_天眼功能统计数据报错 warning警告！！！',
            e,
            datetime.datetime.today()
        )
        celery_error_warning(msg)
    return JsonResponse(response.__dict__)


# 最后活跃时间马上到24小时的 发送消息
def last_active_time(request):
    response = Response.ResponseObj()
    try:
        now = datetime.datetime.today()
        start_time = (now - datetime.timedelta(days=1, minutes=10))
        stop_time = (now - datetime.timedelta(days=1))
        # 最后活跃时间 至当前 差十分钟 满24小时
        objs = models.Userprofile.objects.filter(
            openid__isnull=False,
            last_active_time__isnull=False,
            last_active_time__gte=start_time,
            last_active_time__lte=stop_time,
            is_send_msg=0,                      # 未发送过消息的
        )
        print(start_time, stop_time, now)
        for obj in objs:
            obj.is_send_msg = 1
            obj.save()

            post_data = {
                "touser": obj.openid,
                "msgtype": "text",
                "text": {
                    "content": '天眼将暂停为您推送消息, 微信限制于超过24小时未互动 公众号则不能发送消息\n快来点击下方获客文章解除限制'
                }
            }
            data = get_ent_info(obj.id)
            weixin_objs = WeChatApi(data)

            # 发送客服消息
            post_data = bytes(json.dumps(post_data, ensure_ascii=False), encoding='utf-8')
            weixin_objs.news_service(post_data)
        response.code = 200
    except Exception as e:
        msg = '警告:{}, \n错误:{}, \n时间:{}'.format(
            'celery_活跃即将超时发送消息报错---警告',
            e,
            datetime.datetime.today()
        )
        celery_error_warning(msg)
    return JsonResponse(response.__dict__)


# 客户查看 文章/微店 给用户发送消息
def customer_view_articles_send_msg(request):
    response = Response.ResponseObj()
    print('----------判断 是否能发送')
    try:
        check_type = request.POST.get('check_type')
        title = request.POST.get('title')
        customer_id = request.POST.get('customer_id')
        user_id = request.POST.get('user_id')
        customer_obj = models.Customer.objects.get(id=customer_id)
        user_obj = models.Userprofile.objects.get(id=user_id)

        # 区分普通用户和 会员用户 会员用户发送查看人名称
        print('user_obj.overdue_date--------> ', type(user_obj.overdue_date))
        if user_obj.overdue_date >= datetime.date.today():
            msg = '有人看了您的{}\n《{}》\n查看人:{}\n赶快点击 *天眼* 查看吧！'.format(
                check_type, title, b64decode(customer_obj.name)
            )
        else:
            msg = '有人看了您的{}\n《{}》\n赶快点击 *天眼* 查看吧 ↓↓↓'.format(
                check_type, title
            )

        user_info = get_ent_info(user_id)
        weixin_objs = WeChatApi(user_info)
        post_data = {
                    "touser": user_info.get('openid'),
                    "msgtype": "text",
                    "text": {
                        "content":msg
                    }
            }

        # 发送客服消息
        print('-------------记录最后一次发送时间')
        post_data = bytes(json.dumps(post_data, ensure_ascii=False), encoding='utf-8')
        weixin_objs.news_service(post_data)

        response.code = 200
    except Exception as e:
        msg = '警告:{}, \n错误:{}, \n时间:{}'.format(
            'celery_客户查看 文章/微店 给用户发送消息---警告',
            e,
            datetime.datetime.today()
        )
        celery_error_warning(msg)
    return JsonResponse(response.__dict__)




