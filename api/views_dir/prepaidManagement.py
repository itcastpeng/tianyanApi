import re, requests, hashlib, random, time, json, xml.dom.minidom as xmldom, base64, datetime
from api import models
from publicFunc import Response
from publicFunc import account, xmldom_parsing
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.weixin.weixin_pay_api import micro_public_letter
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi



@csrf_exempt
@account.is_token(models.Userprofile)
def weixin_pay(request, oper_type, o_id):
    response = Response.ResponseObj()
    pub_obj = micro_public_letter()  # 实例 公共函数
    weixin_obj = WeChatApi()
    mch_id = '1488841842'
    SHANGHUKEY = 'fk1hzTGe5G5qt2mlR8UD5AqOgftWuTsK'
    appid = weixin_obj.get_appid()

    # 预支付
    if oper_type == 'yuZhiFu':
        user_id = request.GET.get('user_id')
        fee_objs = models.renewal_management.objects.filter(id=o_id)
        if fee_objs:
            userObjs = models.Userprofile.objects.filter(id=user_id)
            user_obj = userObjs[0]
            fee_obj = fee_objs[0]
            total_fee = int(fee_obj.price) * 100

            data = {
                'appid': appid,             # appid
                'mch_id': mch_id,           # 商户号
                'total_fee': total_fee,     # 金额(分 为单位)
                'openid': user_obj.openid,  # 微信用户唯一标识
                'SHANGHUKEY': SHANGHUKEY,   # 商户KEY
            }
            result = pub_obj.yuzhifu(data)  # 预支付
            return_code = result.get('return_code')
            return_msg = result.get('return_msg')
            dingdanhao = result.get('dingdanhao')
            prepay_id = result.get('prepay_id')

            if return_code == 'SUCCESS':        # 判断预支付返回参数 是否正确
                order_objs = models.renewal_log.objects.filter(pay_order_no=dingdanhao) # 创建订单日志

                renewal_number_days = fee_obj.renewal_number_days # 续费天数
                overdue_date = (user_obj.overdue_date + datetime.timedelta(days=renewal_number_days)) # 续费后 到期时间
                if not order_objs:
                    models.renewal_log.objects.create(
                        pay_order_no=dingdanhao,
                        the_length=fee_obj.get_the_length_display(), # 续费时长
                        renewal_number_days=renewal_number_days,
                        create_user_id=user_id,
                        price=total_fee,
                        original_price=fee_obj.original_price, # 原价
                        overdue_date=overdue_date,
                    )
                response.data = {'prepay_id':prepay_id}
                response.code = 200
                response.msg = '预支付请求成功'
            else:
                response.code = 301
                response.msg = '支付失败, 原因:{}'.format(return_msg)
        else:
            response.code = 301
            response.msg = '请选择一项会员'


    # 微信回调
    elif oper_type == 'wxpay':
        isSuccess = 0
        response.code = 200
        DOMTree = xmldom.parseString(request.body)
        collection = DOMTree.documentElement
        data = ['mch_id', 'return_code', 'appid', 'openid', 'cash_fee', 'out_trade_no']
        resultData = xmldom_parsing.xmldom(collection, data)

        renewal_log_objs = models.renewal_log.objects.filter(pay_order_no=resultData['out_trade_no'])
        if resultData['return_code'] == 'SUCCESS':
            renewal_log_obj = renewal_log_objs[0]

            # 查询订单是否付款成功
            result_data = {
                'appid': resultData['appid'],                   # appid
                'mch_id': resultData['mch_id'],                 # 商户号
                'out_trade_no': resultData['out_trade_no'],     # 订单号
                'nonce_str': pub_obj.generateRandomStamping(),  # 32位随机值
                'SHANGHUKEY': SHANGHUKEY,                       # 商户KEY
            }
            return_code = pub_obj.weixin_back_pay(result_data)

            if return_code == 'SUCCESS':
                isSuccess = 1
                user_objs = models.Userprofile.objects.filter(id=renewal_log_obj.create_user_id)
                user_objs.update(overdue_date=renewal_log_obj.overdue_date)

        renewal_log_objs.update(isSuccess=isSuccess) # 修改订单状态
    return JsonResponse(response.__dict__)
