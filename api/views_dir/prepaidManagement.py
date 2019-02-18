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
def weixin_pay(request, oper_type):
    response = Response.ResponseObj()

    # 预支付
    if oper_type == 'yuZhiFu':
        pub_obj = pub() # 实例 公共函数
        url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'  # 微信支付接口

        user_id = request.GET.get('user_id')

        userObjs = models.Userprofile.objects.filter(id=user_id)

        openid = userObjs[0].openid  # openid  用户标识
        print('openid-----------> ', openid)
        total_fee = 100
        ymdhms = time.strftime("%Y%m%d%H%M%S", time.localtime())  # 年月日时分秒
        shijianchuoafter5 = str(int(time.time() * 1000))[8:]  # 时间戳 后五位
        dingdanhao = str(ymdhms) + shijianchuoafter5 + str(random.randint(10, 99))

        result_data = {
            'appid': 'wx0f55c67abd0ebf3d',  # appid
            'mch_id': '1488841842',  # 商户号
            'nonce_str': pub_obj.generateRandomStamping(),  # 32位随机值a
            'openid': openid,
            'body': 'zhuge-vip',  # 描述
            'out_trade_no': dingdanhao,  # 订单号
            'total_fee': total_fee,  # 金额
            'spbill_create_ip': '0.0.0.0',  # 终端IP
            'notify_url': 'http://tianyan.zhangcong.top/api/wxpay',
            'trade_type': 'JSAPI'
        }

        stringSignTemp = pub_obj.shengchengsign(result_data)
        print('stringSignTemp-------> ', stringSignTemp)
        result_data['sign'] = pub_obj.md5(stringSignTemp).upper()
        print('result_data------------> ', result_data)
        xml_data = pub_obj.toXml(result_data)
        print('xml_data--> ', xml_data)
        ret = requests.post(url, data=xml_data, headers={'Content-Type': 'text/xml'})
        ret.encoding = 'utf8'
        print(ret.text)

        # DOMTree = xmldom.parseString(ret.text)
        # collection = DOMTree.documentElement
        # data = ['return_code', 'return_msg']
        # resultData = xmldom_parsing.xmldom(collection, data)
        #
        # if resultData['return_code'] == 'SUCCESS':        # 判断预支付返回参数 是否正确
        #     data = ['prepay_id']
        #     resultData = xmldom_parsing.xmldom(collection, data)
        #     response.code = 200
        #     response.msg = '预支付请求成功'
        # 预支付成功 创建订单
        #     if not fukuan: # 判断是否已经存在订单
        #         dingDanObjs = models.zgld_shangcheng_dingdan_guanli.objects
        #         date_time = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        #         commissionFee = 0
        #         if goodsObjs[0].commissionFee:
        #             commissionFee = goodsObjs[0].commissionFee
        #
        #         dingDanObjs.create(
        #             shangpinguanli_id = goodsId,            # 商品ID
        #             orderNumber = int(getWxPayOrderId),     # 订单号
        #             yingFuKuan = float(total_fee)/100,      # 应付款
        #             goodsPrice = goodsObjs[0].goodsPrice,   # 商品单价
        #             youHui = 0,                             # 优惠
        #             unitRiceNum=int(goodsNum),              # 数量
        #             yewuUser_id = u_id,                     # 业务
        #             gongsimingcheng_id = company_id,        # 公司
        #             yongJin = commissionFee,                # 佣金
        #             shouHuoRen_id = user_id,                # 收货人
        #             theOrderStatus = 1,                     # 订单状态
        #             createDate=date_time,
        #             goodsName=goodsObjs[0].goodsName,
        #             detailePicture=goodsObjs[0].detailePicture,
        #             phone=phoneNumber
        #         )
        #         # code_url = collection.getElementsByTagName("code_url")[0].childNodes[0].data # 二维码
        #         prepay_id = resultData['prepay_id'] # 直接支付
        #         data_dict = {
        #             # 'appId' : 'wx1add8692a23b5976',
        #             'appId' : appid,
        #             'timeStamp': int(time.time()),
        #             'nonceStr':generateRandomStamping(),
        #             'package': 'prepay_id=' + prepay_id,
        #             'signType': 'MD5'
        #         }
        #         stringSignTemp = shengchengsign(data_dict, SHANGHUKEY)
        #         data_dict['paySign'] = md5(stringSignTemp).upper() # upper转换为大写
        #         response.data = data_dict
        #
        #     return JsonResponse(response.__dict__)
        # else:
        #     if not fukuan:
        #         response.msg = '预支付失败, 原因:{}'.format(resultData['return_msg'])
        #     else:
        #         response.msg = '支付失败, 原因:{}'.format(resultData['return_msg'])
        #
        #     response.code = 301
        #     response.data = ''

    # 微信回调
    elif oper_type == 'wxpay':
        print('------------------------------回调')
        response.code = 200



    return JsonResponse(response.__dict__)