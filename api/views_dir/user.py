from django.shortcuts import render, redirect
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.user import SelectForm
import json
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
import re
import datetime, requests, time
from publicFunc import base64_encryption
from publicFunc.account import get_token
from publicFunc.account import str_encrypt
from publicFunc.host import host_url

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
                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'name': base64_encryption.b64decode(obj.name),
                    'phone_number': obj.phone_number,
                    'signature': obj.signature,
                    'show_product': obj.show_product,
                    'register_date': obj.register_date.strftime('%Y-%m-%d'),
                    'overdue_date': obj.overdue_date.strftime('%Y-%m-%d'),
                    'set_avator': obj.set_avator,
                    'qr_code': obj.qr_code,
                    'brand_list': brand_list,
                    'team_list': team_list,
                    'vip_type': obj.get_vip_type_display(),
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
            classify_id = request.POST.getlist('classify_id[]')
            print('classify_id------> ', classify_id)
            if classify_id:
                recommend_classify_list = [int(i) for i in classify_id]
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
                name = base64_encryption.b64encode(name)
                models.Userprofile.objects.filter(id=user_id).update(name=name)
                response.code = 200
                response.msg = "修改成功"
            else:
                response.code = 301
                response.msg = "姓名传参异常"

        # 修改手机号
        elif oper_type == "update_phone_number":
            phone_number = request.POST.get('phone_number')
            flag = re.match(r"^1\d{10}$", phone_number)      # 验证是否以1开头，并且是11位的数字
            if phone_number and flag:
                models.Userprofile.objects.filter(id=user_id).update(phone_number=phone_number)
                response.code = 200
                response.msg = "修改成功"
            else:
                response.code = 301
                response.msg = "手机号传参异常"

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



    else:
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
                remaining_days = 0
                vip_type = "vip已过期"

            response.code = 200
            response.data = {
                'vip_type': vip_type,
                'overdue_date': obj.overdue_date.strftime('%Y-%m-%d'),
                'remaining_days': remaining_days
            }

            response.note = {
                'vip_type': "vip类型",
                'overdue_date': "有效期至",
                'remaining_days': "剩余天数"
            }

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)


# 用户登录
def user_login_oper(request, oper_type):
    response = Response.ResponseObj()
    weichat_api_obj = WeChatApi()
    # if oper_type == 'login':  # 创建 模板 生成跳转页面
    #     redirect_uri = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/user_login/user_login_get_info'
    #     weixin_url = "https://open.weixin.qq.com/connect/oauth2/authorize?" \
    #                  "appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo" \
    #                  "&state=STATE#wechat_redirect" \
    #         .format(
    #         appid=weichat_api_obj.APPID,
    #         redirect_uri=redirect_uri,
    #     )
    #     key = int(time.time())
    #     menu_data = {
    #         'button':[
    #             {
    #                 'type':'view',
    #                 'name':'天眼',
    #                 'url': weixin_url,
    #                 'key': key
    #             }
    #         ]
    #     }
    #
    #     weichat_api_obj.createMenu(menu_data)

        # weichat_api_obj.deleteMenu()
        # weichat_api_obj.delMenu()
        # data = weichat_api_obj.getMenu()
        # print('data-----> ', data)
        # print('weixin_url------> ', weixin_url)



    # # 判断该用户是否存在
    if oper_type == 'user_login_get_info':
        code = request.GET.get('code')
        objs = models.save_code.objects.filter(save_code=code)
        if not objs:
            models.save_code.objects.create(
                save_code=code
            )

            ret_obj = weichat_api_obj.get_openid(code)  # 获取用户信息
            print('code-----code-------code--------code--------code-------> ', code, ret_obj)
            openid = ret_obj.get('openid')
            user_data = {
                "sex": ret_obj.get('sex'),
                "country": ret_obj.get('country'),
                "province": ret_obj.get('province'),
                "city": ret_obj.get('city'),
            }
            user_objs = models.Userprofile.objects.filter(openid=openid)
            if user_objs:  # 客户已经存在
                user_objs.update(**user_data)
                user_objs = user_objs[0]

            else:  # 不存在，创建用户
                encode_username = base64_encryption.b64encode(
                    ret_obj['nickname']
                )

                # subscribe = ret_obj.get('subscribe')
                #
                # # 如果没有关注，获取个人信息判断是否关注
                # if not subscribe:
                #     weichat_api_obj = WeChatApi()
                #     ret_obj = weichat_api_obj.get_user_info(openid=openid)
                #     subscribe = ret_obj.get('subscribe')

                user_data['set_avator'] = ret_obj.get('headimgurl')
                user_data['subscribe'] = True
                user_data['name'] = encode_username
                user_data['openid'] = ret_obj.get('openid')
                user_data['token'] = get_token()
                user_data['overdue_date'] = datetime.datetime.now() + datetime.timedelta(days=30)
                print("user_data --->", user_data)
                user_objs = models.Userprofile.objects.create(**user_data)

            redirect_url = '{host}?user_id={user_id}&token={token}&classify_type=1'.format(
                host=host_url,
                token=user_objs.token,
                user_id=user_objs.id,
            )
            return redirect(redirect_url)

    return JsonResponse(response.__dict__)
