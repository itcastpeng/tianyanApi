import xml.dom.minidom as xmldom
import datetime, time
from api import models
from publicFunc import Response
from publicFunc import account, xmldom_parsing
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from publicFunc.weixin.weixin_pay_api import weixin_pay_api
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
from publicFunc.article_oper import get_ent_info
from django.db.models import F

@csrf_exempt
@account.is_token(models.Userprofile)
def weixin_pay(request, oper_type, o_id):
    response = Response.ResponseObj()
    weixin_pay_api_obj = weixin_pay_api()  # 实例 公共函数
    # 预支付
    if oper_type == 'yuZhiFu':
        user_id = request.GET.get('user_id')
        fee_objs = models.renewal_management.objects.filter(id=o_id)
        if fee_objs:
            userObjs = models.Userprofile.objects.filter(id=user_id)
            user_obj = userObjs[0]
            fee_obj = fee_objs[0]
            price = int(fee_obj.price)
            # price = int(fee_obj.price) * 100
            data = get_ent_info(user_id)
            weixin_obj = WeChatApi(data)
            appid = weixin_obj.APPID
            data = {
                'total_fee': price,  # 金额(分 为单位)
                'openid': user_obj.openid,  # 微信用户唯一标识
                'appid': appid,  # appid
            }
            result = weixin_pay_api_obj.yuzhifu(data)  # 预支付
            return_code = result.get('return_code')
            return_msg = result.get('return_msg')
            dingdanhao = result.get('dingdanhao')
            prepay_id = result.get('prepay_id')['prepay_id']

            if return_code == 'SUCCESS':  # 判断预支付返回参数 是否正确

                order_objs = models.renewal_log.objects.filter(pay_order_no=dingdanhao)  # 创建订单日志
                renewal_number_days = fee_obj.renewal_number_days  # 续费天数
                overdue_date = (user_obj.overdue_date + datetime.timedelta(days=renewal_number_days))  # 续费后 到期时间
                if not order_objs:
                    models.renewal_log.objects.create(
                        pay_order_no=dingdanhao,
                        the_length=fee_obj.get_the_length_display(),  # 续费时长
                        renewal_number_days=renewal_number_days,
                        create_user_id=user_id,
                        price=price,
                        original_price=fee_obj.original_price,  # 原价
                        overdue_date=overdue_date,
                    )

                data_dict = {
                    'appId': appid,
                    'timeStamp': int(time.time()),
                    'nonceStr': weixin_pay_api_obj.generateRandomStamping(),
                    'package': 'prepay_id=' + prepay_id,
                    'signType': 'MD5'
                }
                SHANGHUKEY = weixin_pay_api_obj.SHANGHUKEY
                stringSignTemp = weixin_pay_api_obj.shengchengsign(data_dict, SHANGHUKEY)
                data_dict['paySign'] = weixin_pay_api_obj.md5(stringSignTemp).upper()  # upper转换为大写

                response.data = data_dict
                response.code = 200
                response.msg = '预支付请求成功'
            else:
                response.code = 301
                response.msg = '支付失败, 原因:{}'.format(return_msg)

        else:
            response.code = 301
            response.msg = '请选择一项会员'

    return JsonResponse(response.__dict__)

    # 微信回调
def payback(request):
    print('------------------微信回调000000000000000000000000000000000000000000000000', request.body)
    weixin_pay_api_obj = weixin_pay_api()  # 实例 公共函数
    response = Response.ResponseObj()
    isSuccess = 0
    response.code = 200
    DOMTree = xmldom.parseString(request.body)
    collection = DOMTree.documentElement
    data = ['mch_id', 'return_code', 'appid', 'openid', 'cash_fee', 'out_trade_no']
    resultData = xmldom_parsing.xmldom(collection, data)
    renewal_log_objs = models.renewal_log.objects.filter(pay_order_no=resultData['out_trade_no'])
    if resultData['return_code'] == 'SUCCESS' and renewal_log_objs:
        renewal_log_obj = renewal_log_objs[0]
        if not renewal_log_obj.isSuccess:
            # 查询订单是否付款成功
            result_data = {
                'appid': resultData['appid'],  # appid
                'mch_id': resultData['mch_id'],  # 商户号
                'out_trade_no': resultData['out_trade_no'],  # 订单号
                'nonce_str': weixin_pay_api_obj.generateRandomStamping(),  # 32位随机值
            }
            return_code = weixin_pay_api_obj.weixin_back_pay(result_data)

            if return_code == 'SUCCESS':
                isSuccess = 1 # 支付状态
                pay_user_id = renewal_log_obj.create_user_id  # 充值人  ID
                renewal_log_objs.update(isSuccess=isSuccess)  # 修改充值成功

                # 修改会员到期时间 和高级会员
                user_objs = models.Userprofile.objects.filter(id=pay_user_id)
                user_objs.update(
                    overdue_date=renewal_log_obj.overdue_date,
                    vip_type=2, # 更改为高级会员
                )

                inviter_id = None  # 父级 推广人
                if user_objs[0].inviter:
                    inviter_id = user_objs[0].inviter_id

                # 判断是否首次充值 判断是否有邀请人 首次充值给 邀请人增钱
                renewal_objs = models.renewal_log.objects.filter(
                    create_user_id=pay_user_id,
                    isSuccess=1
                ) # 充值人为自己 且充值成功
                print('----------------------判断是否首次充值 和 是否有 上线人')
                if renewal_objs.count() == 1 and inviter_id:  # 判断 是否首次充值 和 是否有 上线人
                    print('================================条件满足')
                    price = renewal_objs[0].price / 100  # 首次充值钱数

                    inviter_id_user_obj = models.Userprofile.objects.get(id=inviter_id)
                    if inviter_id_user_obj.vip_type == 2: # 推广人当前为 高级会员
                        print('=-----------------上线人充值 -->', renewal_objs[0].price)
                        cumulative_amount = float(price) * 0.3  # 一级分享人应加钱数  30%
                        print('-----------一级推广人 应给钱数')
                        inviter_id_user_obj.cumulative_amount = F('cumulative_amount') + cumulative_amount  # 累计钱数 + 30%
                        inviter_id_user_obj.make_money = F('make_money') + cumulative_amount                # 待提钱数 + 30%
                        inviter_id_user_obj.save()

                        two_inviter_id = None
                        if inviter_id_user_obj.inviter:
                            two_inviter_id = inviter_id_user_obj.inviter_id
                        if two_inviter_id:
                            print('=-========================二级分享人========================')
                            two_user_obj = models.Userprofile.objects.get(id=two_inviter_id)
                            if two_user_obj.vip_type == 2:
                                cumulative_amount = float(price) * 0.15  # 二级分享人应加钱数
                                print('============================================支付钱数', cumulative_amount)
                                two_user_obj.cumulative_amount = F('cumulative_amount') + cumulative_amount
                                two_user_obj.cumulative_amount = F('make_money') + cumulative_amount
                                two_user_obj.save()

                print('--------------------支付成功-------------')
                models.renewal_log.objects.filter(create_user_id=pay_user_id, isSuccess=0).delete()  # 删除该人原有 未成功 订单
            else:
                objs = models.renewal_log.objects.filter(pay_order_no=result_data.get('out_trade_no'))
                if objs:
                    objs.delete()
                print('------支付失败 ----------删除订单')


            renewal_log_objs.update(isSuccess=isSuccess)  # 修改订单状态
    return JsonResponse(response.__dict__)
