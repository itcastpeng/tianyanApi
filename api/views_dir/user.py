from django.shortcuts import render, redirect
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.user import SelectForm
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
from publicFunc.base64_encryption import b64decode, b64encode
from publicFunc.account import get_token, randon_str
from publicFunc.host import host_url
from publicFunc.article_oper import get_ent_info
from publicFunc.emoji import zhayan, qian
from publicFunc.qiniu_oper import requests_img_download, update_qiniu
from publicFunc.public import verify_mobile_phone_number, pub_log_access, tuiguang
import re, os, json, sys, datetime


# cerf  token验证 用户展示模块
@account.is_token(models.Userprofile)
def user(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            user_id = request.GET.get('user_id')
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'name': '__contains',
                'create_datetime': '',
            }

            q = conditionCom(request, field_dict)

            print('q -->', q)
            objs = models.Userprofile.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []
            for obj in objs:
                # 返回的数据
                team_list = []
                team_objs = models.UserprofileTeam.objects.filter(user_id=obj.id)
                for team_obj in team_objs:
                    team_list.append(team_obj.team_id)
                brand_list = [i['name'] for i in obj.brand_classify.values('name')]
                qr_code = ''
                if obj.qr_code:
                    qr_code = obj.qr_code + '?imageView2/2/w/100'

                set_avator = ''
                inviter_id = ''
                inviter_name = ''
                if obj.inviter:
                    inviter_name = b64decode(obj.inviter.name)
                    inviter_id = obj.inviter_id
                    set_avator = obj.inviter.set_avator + '?imageView2/2/w/100'

                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'name': b64decode(obj.name),
                    'phone_number': obj.phone_number,
                    'signature': obj.signature,
                    'show_product': obj.show_product,
                    'register_date': obj.register_date.strftime('%Y-%m-%d'),
                    'overdue_date': obj.overdue_date.strftime('%Y-%m-%d'),
                    'set_avator': obj.set_avator ,
                    'qr_code': qr_code,
                    'brand_list': brand_list,
                    'team_list': team_list,
                    'vip_type': obj.get_vip_type_display(),

                    'my_references_id': inviter_id,                     # 邀请人ID
                    'my_references_name': inviter_name,      # 我的推荐人名称
                    'my_references_set': set_avator    # 我的推荐人头像
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }
            response.note = {
                'id': "用户id",
                'name': "姓名",
                'phone_number': "手机号",
                'signature': "个性签名",
                'show_product': "文章底部是否显示产品",
                'register_date': "注册时间",
                'overdue_date': "过期时间",
                'set_avator': "头像",
                'qr_code': "微信二维码",
                'vip_type': "会员类型",
                'brand_list': "公司/品牌列表",
                'team_list': "团队ID数组",

                'my_references_id': '邀请人ID',
                'my_references_name': '我的推荐人名称',
                'my_references_set': '我的推荐人头像',
            }
        else:
            print("forms_obj.errors -->", forms_obj.errors)
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


# 增删改
# token验证
@account.is_token(models.Userprofile)
def user_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    print('request.POST -->', request.POST)
    if request.method == "POST":
        # 设置推荐分类
        if oper_type == "update_recommend_classify":
            classify_id = request.POST.get('classify_id[]')
            if classify_id:
                recommend_classify_list = [int(i) for i in json.loads(classify_id)]
                print("recommend_classify_list -->", recommend_classify_list)
                user_obj = models.Userprofile.objects.get(id=user_id)
                user_obj.recommend_classify = recommend_classify_list
                response.code = 200
                response.msg = "设置成功"
            else:
                response.code = 301
                response.msg = "分类id传参异常"

        # 修改头像
        elif oper_type == "update_head_portrait":
            img_path = request.POST.get('img_path')
            if img_path:
                models.Userprofile.objects.filter(id=user_id).update(set_avator=img_path)
                response.code = 200
                response.msg = "修改成功"
            else:
                response.code = 301
                response.msg = "头像不能传参异常"

        # 修改姓名
        elif oper_type == "update_name":
            name = request.POST.get('name')
            if name:
                if len(name) <= 9:
                    name = b64encode(name)
                    models.Userprofile.objects.filter(id=user_id).update(name=name)
                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 301
                    response.msg = '名字最大长度为8'
            else:
                response.code = 301
                response.msg = "姓名传参异常"

        # 修改手机号
        elif oper_type == "update_phone_number":
            phone_number = request.POST.get('phone_number')
            if verify_mobile_phone_number(phone_number):
                models.Userprofile.objects.filter(id=user_id).update(phone_number=phone_number)
                response.code = 200
                response.msg = "修改成功"

            else:
                response.code = 301
                response.msg = "请填写正确手机号"

        # 修改微信二维码
        elif oper_type == "update_qr_code":
            qr_code = request.POST.get('qr_code')
            if qr_code:
                models.Userprofile.objects.filter(id=user_id).update(qr_code=qr_code)
                response.code = 200
                response.msg = "修改成功"
            else:
                response.code = 301
                response.msg = "微信二维码传参异常"

        # 修改个性签名
        elif oper_type == "update_signature":
            signature = request.POST.get('signature')
            if signature:
                models.Userprofile.objects.filter(id=user_id).update(signature=signature)
                response.code = 200
                response.msg = "修改成功"
            else:
                response.code = 301
                response.msg = "个性签名传参异常"

        # 修改文章底部是否显示产品
        elif oper_type == "update_show_product":
            show_product = request.POST.get('show_product')
            flag = re.match(r"^[01]$", show_product)

            if show_product and flag:
                models.Userprofile.objects.filter(id=user_id).update(show_product=int(show_product))
                response.code = 200
                response.msg = "修改成功"
            else:
                response.code = 301
                response.msg = "是否显示产品传参异常"

        # 设置消息提醒
        elif oper_type == 'message_remind_setting':
            objs = models.Userprofile.objects.filter(id=user_id)
            objs.update(message_remind=o_id)
            response.code = 200
            response.msg = '修改成功'

    else:
        # 查询我的会员 有效期 和剩余天数/会员类型
        if oper_type == "member_info":
            obj = models.Userprofile.objects.get(id=user_id)

            # vip 类型
            vip_type = obj.get_vip_type_display()

            # 时间对象 - 年月日时分秒
            now_datetime_obj = datetime.datetime.now()

            # 时间对象 - 年月日
            now_date_obj = datetime.date(now_datetime_obj.year, now_datetime_obj.month, now_datetime_obj.day)

            # 计算剩余天数
            remaining_days = (obj.overdue_date - now_date_obj).days

            # 如果已经过期，则剩余过期时间为0，vip类型为vip已过期
            if remaining_days <= 0:

                if remaining_days == 0:
                    remaining_days = '今'
                else:
                    remaining_days = 0
                    obj.vip_type = 0
                    obj.save()
                    obj = models.Userprofile.objects.get(id=user_id)
                vip_type = obj.get_vip_type_display()

            response.code = 200
            response.data = {
                'vip_type': vip_type,
                'overdue_date': obj.overdue_date.strftime('%Y-%m-%d'),
                'remaining_days': str(remaining_days) + '天'
            }

            response.note = {
                'vip_type': "vip类型",
                'overdue_date': "有效期至",
                'remaining_days': "剩余天数"
            }

        # 使用微信头像
        elif oper_type == 'use_wechat_avatar':
            objs = models.Userprofile.objects.filter(id=user_id)
            path = requests_img_download(objs[0].headimgurl)
            set_avator = update_qiniu(path)
            objs.update(set_avator=set_avator)
            response.code = 200
            response.msg = '修改成功'

        # 推广赚钱 展示数据
        elif oper_type == 'affiliate':
            user_pub_objs = models.Userprofile.objects
            response_data = {}
            user_obj = user_pub_objs.get(id=user_id)

            response_data['cumulative_amount'] = user_obj.cumulative_amount # 累计钱数
            response_data['make_money'] = user_obj.make_money                  # 待提钱数

            invite_objs = user_pub_objs.filter(inviter_id=user_id)
            invite_friend_list = [i.get('id') for i in invite_objs.values('id')] # 该邀请人 邀请的好友ID

            print('invite_friend_list----------> ', invite_friend_list)
            # data_list = []
            # for i in invite_friend_list:
            #     data_list.insert(0, i)
            #     data_list.extend([i.get('id') for i in models.Userprofile.objects.filter(inviter_id=i).values('id')])
            # print('data_list--------------> ', data_list)

            invite_objs = models.Userprofile.objects.filter(id__in=invite_friend_list)
            response_data['invite_number_count'] = invite_objs.count()  # 邀请人数量

            # 查询充值自己分销的钱数
            number_clinch_deal_objs = models.distribute_money_log.objects.filter(
                inviter_id=user_id
            ).order_by('-create_date')

            response_data['number_clinch_count'] = number_clinch_deal_objs.count()  # 成交人数


            if o_id and int(o_id) == 1:  # 邀请人数详情
                invite_number_list = []
                for invite_number_obj in invite_objs:

                    # 该用户未充值展示的话
                    prepaid_text = '用户未开通会员, 邀请付款有现金奖励{}!'.format(qian)
                    if invite_number_obj.renewal_log_set.count() >= 1: # 判断该用户是否充值
                        money_objs = models.distribute_money_log.objects.filter(
                            inviter_id=user_id,
                            user_id=invite_number_obj.id
                        )
                        if money_objs:
                            money = money_objs[0].money
                            prepaid_text = '成为会员, 加入账户{}元!{}'.format(money, qian)

                    invite_number_list.append({
                        'create_user__set_avator': invite_number_obj.set_avator,
                        'name':b64decode(invite_number_obj.name),
                        'prepaid_text':prepaid_text,
                    })
                response_data['invite_number_list'] = invite_number_list

            elif o_id and int(o_id) == 2: # 成交人数
                number_clinch_deal_list = []
                for number_clinch_deal_obj in number_clinch_deal_objs:
                    number_clinch_deal_list.append({
                        'user_set_avator': number_clinch_deal_obj.user.set_avator,
                        'user_name': b64decode(number_clinch_deal_obj.user.name),
                        'price': number_clinch_deal_obj.price,
                        'money': number_clinch_deal_obj.money,
                    })
                response_data['number_clinch_deal_list'] = number_clinch_deal_list


            response.code = 200
            response.msg = '查询成功'
            response.data = response_data
            response.note = {
                'number_clinch_deal_list': {
                    'user_set_avator':'充值人头像',
                    'user_name':'充值人名称',
                    'price':'充值钱数',
                    'money':'应得钱数',

                },
                "invite_number_count": '邀请人数量',
                "cumulative_amount": '累计钱数',
                "make_money": '待提钱数',
                "number_clinch_count": '成交人数',
                "invite_number_list": '邀请人详情',
            }

        # 推广赚钱 二维码截图
        elif oper_type == 'affiliate_screenshots':
            # user_obj = models.Userprofile.objects.get(id=user_id)

            img_path, expire_date = tuiguang(user_id)

            response.code = 200
            response.msg = '生成成功'
            response.data = {
                'path': img_path
            }

        # 查询消息提醒设置
        elif oper_type == 'get_message_remind':
            user_obj = models.Userprofile.objects.get(id=user_id)

            objs = models.Userprofile.message_remind_status
            data_list = []

            for obj in objs:
                is_choose = False
                if obj[0] == user_obj.message_remind:
                    is_choose = True

                data_list.append({
                    'id': obj[0],
                    'name': obj[1],
                    'is_choose': is_choose
                })
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'data_list': data_list
            }

        # 复制昵称
        elif oper_type == 'copy_nickname':
            obj = models.Customer.objects.get(id=o_id)
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'nickname': b64decode(obj.name)
            }

        # 判断该用户是否到期 (到期后不能转发任何东西)
        elif oper_type == 'is_whether':
            obj = models.Userprofile.objects.get(id=user_id)
            now = datetime.date.today()
            flag = False
            if obj.overdue_date >= now:
                flag = True
            response.code = 200
            response.data = {
                'flag': flag
            }

        # 判断是否有手机号
        elif oper_type == 'is_phone':
            obj = models.Userprofile.objects.get(id=user_id)
            flag = False
            if obj.phone_number:
                flag = True

            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'phone': flag
            }

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)


# 用户登录
def user_login_oper(request, oper_type):
    response = Response.ResponseObj()
    # 判断该用户是否存在
    now = datetime.datetime.today()
    models.save_code.objects.filter(
        create_datetime__lt=now
    ).delete()

    code = request.GET.get('code')
    objs = models.save_code.objects.filter(save_code=code)
    if not objs:
        models.save_code.objects.create(
            save_code=code
        )
        data = get_ent_info(1)
        weichat_api_obj = WeChatApi(data)
        ret_obj = weichat_api_obj.get_openid(code)  # 获取用户信息
        encode_username = b64encode(
            ret_obj['nickname']
        )
        openid = ret_obj.get('openid')
        user_data = {
            "sex": ret_obj.get('sex'),
            "country": ret_obj.get('country'),
            "province": ret_obj.get('province'),
            "city": ret_obj.get('city'),
            "headimgurl": ret_obj.get('headimgurl'), # 更新微信头像
            "wechat_name": encode_username,
            "last_active_time": datetime.datetime.today(),
            "is_send_msg": 0, # 互动超时消息 互动过改为未发
        }
        user_objs = models.Userprofile.objects.filter(openid=openid)
        if user_objs:  # 客户已经存在
            user_obj = user_objs[0]
            # uf user_obj.enterprise.status == 1: # 如果后台开启
            if int(user_obj.is_send_msg) == 1: # 解除24小时未互动限制
                post_data = {
                    "touser": user_obj.openid,
                    "msgtype": "text",
                    "text": {
                        "content": """限制已解除, 天眼将继续为您推送消息!{}""".format(zhayan)
                    }
                }
                data = get_ent_info(user_obj.id)
                weixin_objs = WeChatApi(data)

                # 发送客服消息
                post_data = bytes(json.dumps(post_data, ensure_ascii=False), encoding='utf-8')
                weixin_objs.news_service(post_data)

            user_objs.update(**user_data)
            user_objs = user_objs[0]

        else:  # 不存在，创建用户
            path = requests_img_download(ret_obj.get('headimgurl'))
            set_avator = update_qiniu(path) # 上传至七牛云

            # # 如果没有关注，获取个人信息判断是否关注
            # if not subscribe:
            #     weichat_api_obj = WeChatApi()
            #     ret_obj = weichat_api_obj.get_user_info(openid=openid)
            #     subscribe = ret_obj.get('subscribe')

            user_data['last_active_time'] = datetime.datetime.today()
            user_data['wechat_name'] = encode_username
            user_data['set_avator'] = set_avator
            user_data['headimgurl'] = ret_obj.get('headimgurl')
            user_data['subscribe'] = True
            user_data['name'] = encode_username
            user_data['openid'] = ret_obj.get('openid')
            user_data['token'] = get_token()
            user_data['overdue_date'] = datetime.datetime.now() + datetime.timedelta(days=30)
            user_objs = models.Userprofile.objects.create(**user_data)
        user_id = user_objs.id

        pub_log_access(user_id, msg='用户点击公众号菜单栏登录') # 记录访问日志
        redirect_url = '{host}?user_id={user_id}&token={token}&classify_type=1&page_type={page_type}'.format(
            host=host_url,
            token=user_objs.token,
            user_id=user_id,
            page_type=oper_type,
        )
        print('redirect_url----------------------------> ', redirect_url)
        return redirect(redirect_url)

    else:
        response.code = 301
        response.msg = '请重新登录'


    return JsonResponse(response.__dict__)
