from publicFunc import Response
from django.http import JsonResponse
from publicFunc.weixin.weixin_gongzhonghao_api import pub
from publicFunc.weixin import weixin_gongzhonghao_api
import json, time, hashlib


# 权限签名算法(转发朋友圈等)
def letter_operation(request, oper_type):
    response = Response.ResponseObj()
    if oper_type == 'js_sdk_permissions':
        weixin_obj = weixin_gongzhonghao_api.WeChatApi()
        jsapi_ticket = weixin_obj.get_jsapi_ticket()
        get_signature = weixin_obj.get_signature(jsapi_ticket)
        print('get_signature-> ', get_signature)

        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'get_signature':get_signature
        }
    return JsonResponse(response.__dict__)












