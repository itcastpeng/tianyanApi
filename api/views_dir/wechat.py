#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com


from django.shortcuts import render, HttpResponse
from django.http import JsonResponse

from api import models
import base64
import time
import datetime
import json
import xml.dom.minidom

from publicFunc.account import get_token
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
from publicFunc.Response import ResponseObj


def wechat(request):
    weichat_api_obj = WeChatApi()

    signature = request.GET.get("signature")
    timestamp = request.GET.get("timestamp")
    nonce = request.GET.get("nonce")
    echostr = request.GET.get("echostr")

    # 该值做消息解密使用，当前未使用加密模式，参考微信开发文档 https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421135319
    # EncodingAESKey = 'LFYzOBp42g5kwgSUWhGC9uRugSmpyetKfAsJa5FdFHX'

    check_result = weichat_api_obj.checkSignature(timestamp, nonce, signature)
    print('check_result -->', check_result)

    if check_result:

        if request.method == "GET":
            return HttpResponse(echostr)
        else:
            body_text = str(request.body, encoding="utf8")
            print('body_text -->', body_text)

            # 使用minidom解析器打开 XML 文档
            DOMTree = xml.dom.minidom.parseString(body_text)
            collection = DOMTree.documentElement
            print('collection -->', collection)

            # 事件类型
            event = collection.getElementsByTagName("Event")[0].childNodes[0].data
            print("event -->", event)

            # 用户的 openid
            openid = collection.getElementsByTagName("FromUserName")[0].childNodes[0].data

            # 扫描带参数的二维码
            if event in ["subscribe", "SCAN"]:
                # subscribe = 首次关注
                # SCAN = 已关注
                # 事件 Key 值
                event_key = collection.getElementsByTagName("EventKey")[0].childNodes[0].data
                if event == "subscribe":
                    event_key = event_key.split("qrscene_")[-1]
                event_key = json.loads(event_key)
                inviter_user_id = event_key.get('inviter_user_id')      # 邀请人id
                print('event_key -->', event_key)

                # 保证1个微信只能够关联1个账号
                user_objs = models.Userprofile.objects.filter(openid=openid)
                ret_obj = weichat_api_obj.get_user_info(openid=openid)

                print('ret_obj -->', ret_obj)
                """
                    {
                        'subscribe_scene': 'ADD_SCENE_QR_CODE', 
                            'city': '丰台', 
                        'openid': 'oX0xv1pJPEv1nnhswmSxr0VyolLE', 
                        'qr_scene': 0, 
                        'tagid_list': [], 
                        'nickname': '张聪', 
                        'subscribe_time': 1527689396, 
                            'country': '中国', 
                        'groupid': 0, 
                        'subscribe': 1, 
                        'qr_scene_str': '{"timestamp": "1527689369548"}', 
                        'headimgurl': 'http://thirdwx.qlogo.cn/mmopen/oFswpUmYn53kTv5QdmmONicVJqp3okrhHospu6icoLF7Slc5XyZWR96STN9RiakoBQn1uoFJIWEicJgJ1QjR5iaGOgWNQ5BSVqFe5/132', 
                            'province': '北京', 
                            'sex': 1, 
                        'language': 'zh_CN', 
                        'remark': ''
                    }
                """

                user_data = {
                    "sex": ret_obj['sex'],
                    "country": ret_obj['country'],
                    "province": ret_obj['province'],
                    "city": ret_obj['city'],
                }

                if user_objs:
                    user_objs.update(**user_data)
                else:
                    encodestr = base64.b64encode(ret_obj['nickname'].encode('utf-8'))
                    encode_username = str(encodestr, encoding='utf-8')
                    overdue_date = datetime.datetime.now() + datetime.timedelta(days=30)

                    user_data['inviter_id'] = inviter_user_id
                    user_data['set_avator'] = ret_obj['headimgurl']
                    user_data['name'] = encode_username
                    user_data['openid'] = ret_obj['openid']
                    user_data['overdue_date'] = overdue_date
                    user_data['token'] = get_token()
                    print("user_data --->", user_data)
                    models.Userprofile.objects.create(**user_data)

            # 取消关注
            elif event == "unsubscribe":
                models.Userprofile.objects.filter(openid=openid).update(openid=None)

                # we_chat_public_send_msg_obj.sendTempMsg(post_data)

            return HttpResponse("")

    else:
        return HttpResponse(False)


# @csrf_exempt
# def wechat_login(request):
#     response = ResponseObj()
#     timestamp = request.POST.get('timestamp')
#     user_objs = models.zhugedanao_userprofile.objects.select_related('level_name').filter(timestamp=timestamp)
#     if user_objs:
#         user_obj = user_objs[0]
#         response.code = 200
#         decode_username = base64.b64decode(user_obj.username)
#         username = str(decode_username, 'utf-8')
#         role_id = ''
#         if user_obj.role:
#             role_id = user_obj.role.id
#         response.data = {
#             'token': user_obj.token,
#             'user_id': user_obj.id,
#             'set_avator': user_obj.set_avator,
#             'role_id':role_id,
#             'username':username,
#             'level_name': user_obj.level_name.name
#         }
#         response.msg = "登录成功"
#     else:
#         response.code = 405
#         response.msg = '扫码登录异常，请重新扫描'
#
#     return JsonResponse(response.__dict__)


# 获取用于登录的微信二维码
def weichat_generate_qrcode(request):
    weichat_api_obj = WeChatApi()
    response = ResponseObj()
    inviter_user_id = request.GET.get('inviter_user_id')
    qc_code_url = weichat_api_obj.generate_qrcode({'inviter_user_id': inviter_user_id})
    print(qc_code_url)

    response.code = 200
    response.data = {
        'qc_code_url': qc_code_url,
        'timestamp': inviter_user_id
    }

    return JsonResponse(response.__dict__)
