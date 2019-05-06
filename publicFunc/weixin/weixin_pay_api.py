
import time
import random, uuid
import requests
import xml.dom.minidom as xmldom
from publicFunc import xmldom_parsing
from publicFunc.weixin.weixin_api_public import WeixinApiPublic
import xml, json


class weixin_pay_api(WeixinApiPublic):
    def __init__(self):
        self.mch_id = '1488841842'      # 支付商户号
        self.SHANGHUKEY = '6d5fhg6fdh51gf1h23dfsg5fds54g111'        # 商户api 密钥

    # 生成订单号
    def shengcheng_dingdanhao(self):
        ymdhms = time.strftime("%Y%m%d%H%M%S", time.localtime())  # 年月日时分秒
        timestamp_after_five = str(int(time.time() * 1000))[8:]  # 时间戳 后五位
        dingdanhao = timestamp_after_five + str(ymdhms) + str(random.randint(10, 99))
        return dingdanhao

    # 预支付功能
    def yuzhifu(self, data):
        openid = data.get('openid')
        total_fee = data.get('total_fee')
        appid = data.get('appid')
        url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'  # 微信支付接

        dingdanhao = self.shengcheng_dingdanhao()       # 生成订单号
        result_data = {
            'appid': appid,                             # appid
            'mch_id': self.mch_id,                      # 商户号
            'nonce_str': self.generateRandomStamping(), # 32位随机值
            'openid': openid,                           # 微信用户唯一标识
            'body': 'tianYan-VIP',                      # 描述
            'out_trade_no': dingdanhao,                 # 订单号
            'total_fee': total_fee,                     # 金额(分 为单位)
            'spbill_create_ip': '0.0.0.0',              # 终端IP
            'notify_url': 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/payback',
            'trade_type': 'JSAPI'                    # 支付方式  NATIVE--Native支付、APP--app支付，MWEB--H5支付
        }
        print('result_data===========> ', result_data)
        string_sign_temp = self.shengchengsign(result_data, self.SHANGHUKEY)
        result_data['sign'] = self.md5(string_sign_temp).upper()
        xml_data = self.toXml(result_data)
        print('xml_data=-xml_data-----------xml_data---------------------------> ', xml_data)
        ret = requests.post(url, data=xml_data, headers={'Content-Type': 'text/xml'})
        ret.encoding = 'utf8'
        print('ret.text---------------ret.text----------------ret.text------------------> ', ret.text)
        dom_tree = xmldom.parseString(ret.text)
        collection = dom_tree.documentElement
        print('collection-------------> ', collection)
        data = ['return_code', 'return_msg']
        result_data = xmldom_parsing.xmldom(collection, data)
        data = ['prepay_id']
        prepay_id = xmldom_parsing.xmldom(collection, data)
        ret_data = {
            'return_code': result_data['return_code'],
            'return_msg': result_data['return_msg'],
            'dingdanhao': dingdanhao,
            'prepay_id': prepay_id,
        }
        return ret_data

    # 回调 判断是否支付成功
    def weixin_back_pay(self, result_data):
        url = 'https://api.mch.weixin.qq.com/pay/orderquery'
        string_sign_temp = self.shengchengsign(result_data, self.SHANGHUKEY)
        result_data['sign'] = self.md5(string_sign_temp).upper()
        xml_data = self.toXml(result_data)
        ret = requests.post(url, data=xml_data, headers={'Content-Type': 'text/xml'})
        ret.encoding = 'utf8'
        dom_tree = xmldom.parseString(ret.text)
        collection = dom_tree.documentElement
        return_code = collection.getElementsByTagName("return_code")[0].childNodes[0].data

        return return_code

    def generateRandomStamping(self):
        return str(uuid.uuid4()).replace('-', '')


    # 提现
    def withdrawal(self, data):
        print('self.mch_id-------------> ', self.mch_id, data.get('appid'))
        url = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/sendredpack'
        result_data = {
            'nonce_str': self.generateRandomStamping(),     # 32位随机值a
            'mch_billno': data.get('dingdanhao'),           # 订单号
            'wxappid': data.get('appid'),                   # appid
            'mch_id': self.mch_id,                          # 商户号
            # 'send_name': '眼'.encode('utf8'),          # 商家名称
            'send_name': 'tianyan',                     # 商家名称
            're_openid':data.get('openid'),                 # openid
            'total_num':1,                                  # 发放红包总人数
            'total_amount':data.get('withdrawal_amount') * 100,   # 提现金额
            'wishing':'tianyan_tixian',                    # 提现金额
            # 'wishing':'感谢您使用微商天眼'.encode('utf8'),                    # 提现金额
            'client_ip':'0.0.0.0',                          # IP地址
            # 'act_name':'提现'.encode('utf8'),                        # 活动名称
            'act_name':'tianyanhuodong',                        # 活动名称
            # 'remark':'快来邀请好友推广赚钱吧!'.encode('utf8'),                # 备注
            'remark':'tianyan_beizhu!',                # 备注
            'scene_id':'PRODUCT_5',                         # 场景ID 渠道分润
        }

        string_sign_temp = self.shengchengsign(result_data, self.SHANGHUKEY)
        result_data['sign'] = self.md5(string_sign_temp).upper()
        xml_data = self.toXml(result_data)
        print('xml_data--------> ', xml_data)
        apiclient_key = 'statics/zhengshu/apiclient_key.pem'
        apiclient_cert = 'statics/zhengshu/apiclient_cert.pem'

        ret = requests.post(url, data=xml_data, verify=False, cert=(apiclient_cert, apiclient_key))
        ret.encoding = 'utf-8'
        print('提现 ret.text---> ', ret.text)
        dom_tree = xmldom.parseString(ret.text)
        collection = dom_tree.documentElement
        data = ['err_code', 'return_msg']
        result_data = xmldom_parsing.xmldom(collection, data)
        if result_data.get('err_code') == 0 and result_data.get('return_msg') == '发放成功.':
            print('------------提现成功')
        else:
            print('result_data======> ', result_data)













