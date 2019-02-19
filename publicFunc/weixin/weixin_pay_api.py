
import hashlib, uuid, time, random

class pub(object):
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

