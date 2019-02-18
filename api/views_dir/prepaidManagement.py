import re, requests, hashlib, random, uuid, time, json, xml.dom.minidom as xmldom, base64, datetime
from api import models
from publicFunc import Response
from publicFunc import account, xmldom_parsing
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect


class pub(object):
    def __init__(self):
        pass

    def md5(self, string):
        m = hashlib.md5()
        m.update(string.encode('utf8'))
        return m.hexdigest()

    # 返回 xml
    def toXml(self, params):
        xml = []
        for k in sorted(params.keys()):
            v = params.get(k)
            if k == 'detail' and not v.startswith('<![CDATA['):
                v = '<![CDATA[{}]]>'.format(v)
            xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
        return '<xml>{}</xml>'.format(''.join(xml))

    # 返回32为 时间戳
    def generateRandomStamping(self):
        return str(uuid.uuid4()).replace('-', '')

    # 生成二维码
    # def create_qrcode(self, url):
    #     img = qrcode.make(url)
    #     img.get_image().show()
    #     img.save('hello.png')

    # 生成 签名
    def shengchengsign(self, result_data, KEY=None):
        ret = []
        for k in sorted(result_data.keys()):
            if (k != 'sign') and (k != '') and (result_data[k] is not None):
                ret.append('%s=%s' % (k, result_data[k]))
        stringA = '&'.join(ret)
        stringSignTemp = stringA
        if KEY:
            stringSignTemp = '{stringA}&key={key}'.format(
                stringA=stringA,
                key=KEY
            )
        return stringSignTemp




@csrf_exempt
def weixin_pay(request, oper_type, o_id):
    response = Response.ResponseObj()
    pub_obj = pub()  # 实例 公共函数
    SHANGHUKEY = 'fk1hzTGe5G5qt2mlR8UD5AqOgftWuTsK'
    appid = 'wx0f55c67abd0ebf3d'
    mch_id = '1488841842'

    # 预支付
    if oper_type == 'yuZhiFu':
        user_id = request.POST.get('user_id')
        fee_objs = models.renewal_management.objects.filter(id=o_id)
        if fee_objs:
            userObjs = models.Userprofile.objects.filter(id=user_id)
            user_obj = userObjs[0]
            fee_obj = fee_objs[0]


            url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'  # 微信支付接口

            ymdhms = time.strftime("%Y%m%d%H%M%S", time.localtime())  # 年月日时分秒
            shijianchuoafter5 = str(int(time.time() * 1000))[8:]  # 时间戳 后五位
            dingdanhao = shijianchuoafter5 + str(ymdhms) + str(random.randint(10, 99))

            total_fee = int(fee_obj.price) * 100

            result_data = {
                'appid': appid,                                 # appid
                'mch_id': mch_id,                               # 商户号
                'nonce_str': pub_obj.generateRandomStamping(),  # 32位随机值a
                'openid': user_obj.openid,                      # 微信用户唯一标识
                'body': '天眼-会员续费'.encode('utf8'),           # 描述
                'out_trade_no': dingdanhao,                     # 订单号
                'total_fee': total_fee,                         # 金额(分 为单位)
                'spbill_create_ip': '0.0.0.0',                  # 终端IP
                'notify_url': 'http://api.zhugeyingxiao.com/tianyan/wxpay', # 指向--> http://127.0.0.1:8008/api/weixin_pay/wxpay
                'trade_type': 'JSAPI'
            }

            stringSignTemp = pub_obj.shengchengsign(result_data, KEY=SHANGHUKEY)
            result_data['sign'] = pub_obj.md5(stringSignTemp).upper()

            xml_data = pub_obj.toXml(result_data)
            ret = requests.post(url, data=xml_data, headers={'Content-Type': 'text/xml'})
            ret.encoding = 'utf8'

            DOMTree = xmldom.parseString(ret.text)
            collection = DOMTree.documentElement
            data = ['return_code', 'return_msg']
            resultData = xmldom_parsing.xmldom(collection, data)
            if resultData['return_code'] == 'SUCCESS':        # 判断预支付返回参数 是否正确
                data = ['prepay_id']

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
                response.data = {'prepay_id':xmldom_parsing.xmldom(collection, data)}
                response.code = 200
                response.msg = '预支付请求成功'
            else:
                response.code = 301
                response.msg = '支付失败, 原因:{}'.format(resultData['return_msg'])
        else:
            response.code = 301
            response.msg = '请选择一项会员'


    # 微信回调
    elif oper_type == 'wxpay':
        isSuccess = 0
        print('------------------------------回调-----------------------')
        response.code = 200
        print('request.body---------> ', request.body)
        DOMTree = xmldom.parseString(request.body)
        collection = DOMTree.documentElement
        data = ['mch_id', 'return_code', 'appid', 'openid', 'cash_fee', 'out_trade_no']
        resultData = xmldom_parsing.xmldom(collection, data)

        renewal_log_objs = models.renewal_log.objects.filter(pay_order_no=resultData['out_trade_no'])
        if resultData['return_code'] == 'SUCCESS':
            renewal_log_obj = renewal_log_objs[0]

            # 查询订单是否付款成功
            result_data = {
                'appid': resultData['appid'],  # appid
                'mch_id': resultData['mch_id'],  # 商户号
                'out_trade_no': resultData['out_trade_no'],  # 订单号
                'nonce_str': pub_obj.generateRandomStamping(),  # 32位随机值
            }
            url = 'https://api.mch.weixin.qq.com/pay/orderquery'
            stringSignTemp = pub_obj.shengchengsign(result_data, SHANGHUKEY)
            result_data['sign'] = pub_obj.md5(stringSignTemp).upper()
            xml_data = pub_obj.toXml(result_data)
            ret = requests.post(url, data=xml_data, headers={'Content-Type': 'text/xml'})
            ret.encoding = 'utf8'
            print('ret.text------------> ', ret.text)
            DOMTree = xmldom.parseString(ret.text)
            collection = DOMTree.documentElement
            return_code = collection.getElementsByTagName("return_code")[0].childNodes[0].data
            if return_code == 'SUCCESS':
                isSuccess = 1
                user_objs = models.Userprofile.objects.filter(id=renewal_log_obj.create_user_id)
                user_objs.update(overdue_date=renewal_log_obj.overdue_date)

        renewal_log_objs.update(isSuccess=isSuccess) # 修改订单状态
    return JsonResponse(response.__dict__)
