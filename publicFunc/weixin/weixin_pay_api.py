
import hashlib, uuid, time, random, requests, xml.dom.minidom as xmldom
from publicFunc import account, xmldom_parsing
class micro_public_letter(object):
    def __init__(self):
        pass

    def sha1(self, string):
        return hashlib.sha1(string.encode('utf8')).hexdigest()


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

    # 生成订单号
    def shengcheng_dingdanhao(self):
        ymdhms = time.strftime("%Y%m%d%H%M%S", time.localtime())  # 年月日时分秒
        timestamp_after_five = str(int(time.time() * 1000))[8:]  # 时间戳 后五位
        dingdanhao = timestamp_after_five + str(ymdhms) + str(random.randint(10, 99))
        return dingdanhao

    # 预支付功能
    def yuzhifu(self, data):
        appid = data.get('appid')
        mch_id = data.get('mch_id')
        openid = data.get('openid')
        total_fee = data.get('total_fee')
        SHANGHUKEY = data.get('SHANGHUKEY')
        url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'  # 微信支付接

        dingdanhao = self.shengcheng_dingdanhao()       # 生成订单号
        result_data = {
            'appid': appid,                             # appid
            'mch_id': mch_id,                           # 商户号
            'nonce_str': self.generateRandomStamping(), # 32位随机值a
            'openid': openid,                           # 微信用户唯一标识
            'body': '天眼-会员续费'.encode('utf8'),       # 描述
            'out_trade_no': dingdanhao,                 # 订单号
            'total_fee': total_fee,                     # 金额(分 为单位)
            'spbill_create_ip': '0.0.0.0',              # 终端IP
            'notify_url': 'http://api.zhugeyingxiao.com/tianyan/wxpay', # 指向--> http://127.0.0.1:8008/api/weixin_pay/wxpay
            'trade_type': 'JSAPI'
        }
        stringSignTemp = self.shengchengsign(result_data, KEY=SHANGHUKEY)
        result_data['sign'] = self.md5(stringSignTemp).upper()
        xml_data = self.toXml(result_data)
        ret = requests.post(url, data=xml_data, headers={'Content-Type': 'text/xml'})
        ret.encoding = 'utf8'

        DOMTree = xmldom.parseString(ret.text)
        collection = DOMTree.documentElement
        data = ['return_code', 'return_msg']
        resultData = xmldom_parsing.xmldom(collection, data)
        data = ['prepay_id']
        prepay_id = xmldom_parsing.xmldom(collection, data)
        ret_data = {
            'return_code':resultData['return_code'],
            'return_msg':resultData['return_msg'],
            'dingdanhao':dingdanhao,
            'prepay_id':prepay_id,
        }
        return ret_data


    # 回调 判断是否支付成功
    def weixin_back_pay(self, result_data):
        SHANGHUKEY = result_data['SHANGHUKEY']
        url = 'https://api.mch.weixin.qq.com/pay/orderquery'
        stringSignTemp = self.shengchengsign(result_data, SHANGHUKEY)
        result_data['sign'] = self.md5(stringSignTemp).upper()
        xml_data = self.toXml(result_data)
        ret = requests.post(url, data=xml_data, headers={'Content-Type': 'text/xml'})
        ret.encoding = 'utf8'
        DOMTree = xmldom.parseString(ret.text)
        collection = DOMTree.documentElement
        return_code = collection.getElementsByTagName("return_code")[0].childNodes[0].data

        return return_code






