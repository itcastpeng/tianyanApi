from api import models
from publicFunc import Response
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from publicFunc.base64_encryption import b64decode, b64encode
from publicFunc.article_oper import get_ent_info
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
from publicFunc.user import is_send_msg
from django.db.models import F
from publicFunc.emoji import xiajiantou, nanshou, caidai
from publicFunc.qiniu_oper import update_qiniu, requests_img_download
from publicFunc.get_content_article import get_article
import datetime, json, time, requests

# 报错警告  celery捕获异常 发送客服消息 到管理员
def celery_error_warning(msg, external=None): #external 外部引用
    print('*********!!!!!!!!!!!!!!!!!!!!!!!!!!!!!******************!!!!!!!!!!!!!!!!!!!!!!*************!!!!!!!!!!', msg)
    user_info = get_ent_info(1)
    weixin_objs = WeChatApi(user_info)

    openid_list = [
        'oX0xv1iqlzEtIhkeutd6f_wzAEpM', # 赵欣鹏
        'oX0xv1pmPrR24l6ezv4mI9HE0-ME', # 小明
    ]
    if external:
        openid_list.append(
            'oX0xv1lvwu7ntr4dJloHtsQdlWkY', # 韩新颖
        )
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


# 外部调用 发送消息
def outside_calls_send_msg(request):
    try:
        msg = request.GET.get('msg')
        if msg:
            msg = '外界消息提醒:' + msg
            is_external = request.GET.get('external')  # 是否为外部
            celery_error_warning(msg, is_external)

    except Exception as e:
        msg = '警告:{}, \n错误:{}, \n时间:{}'.format(
            'celery内 外部调用发送消息报错',
            e,
            datetime.datetime.today()
        )
        celery_error_warning(msg)

    return HttpResponse('')






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
    redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/user_login/mingpian'
    mingpian_url = "https://open.weixin.qq.com/connect/oauth2/authorize?" \
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
                        "url": mingpian_url
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

            for i in data_list:  # 加入数据库
                eye_objs = models.day_eye_celery.objects.filter(
                    user_id=user_id,
                    status=i.get('status'),
                    customer_id=i.get('customer_id'),
                )

                create_date = i.get('create_date')

                if eye_objs:
                    if eye_objs[0].last_click_customer:

                        # 如果 查看时间 大于 用户最后一次点击 该客户时间  为新消息
                        if datetime.datetime.strptime(create_date, '%Y-%m-%d %H:%M:%S') >= eye_objs[0].last_click_customer:
                            is_new_msg = True
                        else:
                            is_new_msg = eye_objs[0].is_new_msg
                    else:
                        is_new_msg = True

                    eye_objs.update(
                        text = i.get('text'),
                        create_date = create_date,
                        is_new_msg = is_new_msg,
                    )
                else:
                    models.day_eye_celery.objects.create(
                        user_id=user_id,
                        status=i.get('status'),
                        customer_id=i.get('customer_id'),
                        text=i.get('text'),
                        create_date=create_date,
                        is_new_msg=True, # 新查看消息提示
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
        stop_Yesterday = (now - datetime.timedelta(days=1))
        start_Yesterday = (now - datetime.timedelta(days=1, minutes=5))

        # 最后活跃时间 至当前 差5分钟 满24小时
        objs = models.Userprofile.objects.filter(
            openid__isnull=False,
            last_active_time__isnull=False,
            is_send_msg=0,                      # 未发送过消息的
        )
        for obj in objs:
            last_active_time = obj.last_active_time
            if last_active_time >= start_Yesterday and last_active_time <= stop_Yesterday:
                obj.is_send_msg = 1
                obj.save()

                print('----------------e----马上超过24小时, 发送消息', obj.id)
                emj = caidai + xiajiantou + caidai
                post_data = {
                    "touser": obj.openid,
                    "msgtype": "text",
                    "text": {
                        "content": """天眼将暂停为您推送消息!\n微信限制于超过24小时未互动,公众号则不能发送消息{}\n快来点击下方获客文章解除限制吧！！\n{}""".format(
                            nanshou, emj
                        )
                    }
                }
                data = get_ent_info(obj.id)
                weixin_objs = WeChatApi(data)

                # 发送客服消息
                post_data = bytes(json.dumps(post_data, ensure_ascii=False), encoding='utf-8')
                weixin_objs.news_service(post_data)
                response.code = 200
            else:
                continue
    except Exception as e:
        msg = '警告:{}, \n错误:{}, \n时间:{}'.format(
            'celery_活跃即将超时发送消息报错---警告',
            e,
            datetime.datetime.today()
        )
        celery_error_warning(msg)
    return JsonResponse(response.__dict__)


# 客户查看 文章/微店 给用户发送消息  可以发送立即发送  不可以发送保存数据库 定时器发送
def customer_view_articles_send_msg(request):
    response = Response.ResponseObj()
    try:
        check_type = request.POST.get('check_type')
        title = request.POST.get('title')
        customer_id = request.POST.get('customer_id')
        user_id = request.POST.get('user_id')

        if is_send_msg(user_id):
            user_obj = models.Userprofile.objects.get(id=user_id)
            customer_obj = models.Customer.objects.get(id=customer_id)

            # 区分普通用户和 会员用户 会员用户发送查看人名称
            if user_obj.overdue_date >= datetime.date.today():
                msg = '有人看了您的{}\n\n《{}》\n查看人:{}\n\n查看点击下方【天眼】\n{}'.format(
                    check_type, title, b64decode(customer_obj.name), xiajiantou
                )
            else:
                msg = '有人看了您的{}\n\n《{}》\n\n查看点击下方【天眼】\n{}'.format(
                    check_type, title, xiajiantou
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
            user_obj.last_message_remind_time = datetime.datetime.now()
            user_obj.save()
            response.code = 200
        else:
            send_msg_objs = models.summary_message_reminder.objects.filter(
                user_id=user_id,
                customer_id=customer_id,
                title=title,
                check_type=check_type,
                is_send=0
            )
            if send_msg_objs:
                send_msg_objs.update(
                    select_num = F('select_num') + 1
                )
            else:
                models.summary_message_reminder.objects.create(
                    user_id=user_id,
                    customer_id=customer_id,
                    title=title,
                    check_type=check_type,
                )
    except Exception as e:
        msg = '警告:{}, \n错误:{}, \n时间:{}'.format(
            'celery_客户查看 文章/微店 给用户发送消息---警告',
            e,
            datetime.datetime.today()
        )
        celery_error_warning(msg)
    return JsonResponse(response.__dict__)


# 汇总消息 发送
def summary_message_reminder_celery(request):
    response = Response.ResponseObj()
    try:
        user_objs = models.Userprofile.objects.exclude(
            message_remind=4
        )
        for user_obj in user_objs:
            if is_send_msg(user_obj.id): # 如果此用户可以发送 消息
                objs = models.summary_message_reminder.objects.select_related('user').filter(
                    is_send=0,
                    user_id=user_obj.id,
                )

                title_str = ''
                for obj in objs:
                    title_str += '《{}》--{}查看{}次\n'.format(
                        obj.title,
                        b64decode(obj.customer.name),
                        obj.select_num
                    )
                    obj.is_send = 1
                    obj.save()

                if title_str: # 如果有文字发送

                    # 区分普通用户和 会员用户 会员用户发送查看人名称
                    if user_obj.overdue_date >= datetime.date.today():
                        msg = '有人看了您多篇文章\n\n{}\n查看点击下方【天眼】\n{}'.format(title_str, xiajiantou)  # 充值用户显示所有文章标题
                    else:
                        msg = '有人看了您多篇文章\n\n赶快点击下方【天眼】查看\n{}'.format(xiajiantou) # 未充值

                    user_info = get_ent_info(user_obj.id)
                    weixin_objs = WeChatApi(user_info)
                    post_data = {
                        "touser": user_info.get('openid'),
                        "msgtype": "text",
                        "text": {
                            "content": msg
                        }
                    }

                    # 发送客服消息
                    post_data = bytes(json.dumps(post_data, ensure_ascii=False), encoding='utf-8')
                    weixin_objs.news_service(post_data)
                    user_obj.last_message_remind_time = datetime.datetime.now()
                    user_obj.save()

                    response.code = 200
            else:
                continue
    except Exception as e:
        msg = '警告:{}, \n错误:{}, \n时间:{}'.format(
            'celery_汇总消息 发送---警告',
            e,
            datetime.datetime.today()
        )
        celery_error_warning(msg)
    return JsonResponse(response.__dict__)

# 更新客户头像到七牛云
def update_customer_set_avator(request):
    objs = models.Customer.objects.filter(set_avator__isnull=False)
    for obj in objs:
        if 'http://tianyan.zhugeyingxiao.com' not in obj.set_avator:
            set_avator = requests_img_download(obj.set_avator)
            set_avator = update_qiniu(set_avator)
            obj.set_avator = set_avator
            obj.save()
    return HttpResponse('')

# 定时更新文章 (主要更新视频)
def celery_regularly_update_articles(request):
    objs = models.Article.objects.filter(original_link__isnull=False)
    for obj in objs:
        data = get_article(obj.original_link, get_content=1)
        obj.content = data.get('content')
        obj.save()
    return HttpResponse('')

