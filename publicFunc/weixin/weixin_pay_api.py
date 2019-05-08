from publicFunc import xmldom_parsing
from publicFunc.weixin.weixin_api_public import WeixinApiPublic
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
from publicFunc.article_oper import get_ent_info
import xml, json, os, xml.dom.minidom as xmldom, requests, random, uuid, time, datetime

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
    def withdrawal(self, result):
        user_id = result.get('user_id')
        user_name = result.get('user_name')
        make_money = result.get('make_money') # 用户待提钱数
        withdrawal_amount = int(result.get('withdrawal_amount'))

        now_datetime = datetime.datetime.today()
        url = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/sendredpack'
        result_data = {
            'nonce_str': self.generateRandomStamping(),  # 32位随机值a
            'mch_billno': result.get('dingdanhao'),      # 订单号
            'mch_id': self.mch_id,                       # 商户号
            'wxappid': result.get('appid'),              # 公众号appid
            're_openid':result.get('openid'),            # openid
            'total_amount':withdrawal_amount * 100,      # 提现金额 分为单位
            'total_num':1,                               # 发放红包总人数
            'client_ip':'0.0.0.0',                       # IP地址
            'send_name': '微商天眼',                      # 商家名称
            'wishing':'提现到账,大吉大利!',                  # 红包祝福语
            'act_name':'tianyanhuodong',                 # 活动名称
            'remark':'tianyan_beizhu!',                  # 备注
        }
        string_sign_temp = self.shengchengsign(result_data, self.SHANGHUKEY)
        result_data['sign'] = self.md5(string_sign_temp).upper()
        xml_data = self.toXml(result_data)

        apiclient_key = os.path.join('statics', 'zhengshu', 'apiclient_key.pem')
        apiclient_cert = os.path.join('statics', 'zhengshu', 'apiclient_cert.pem')

        apiclient_key = 'statics/zhengshu/apiclient_key.pem'
        apiclient_cert = 'statics/zhengshu/apiclient_cert.pem'

        ret = requests.post(url, data=xml_data, verify=False, cert=(apiclient_cert, apiclient_key))
        ret.encoding = 'utf-8'
        dom_tree = xmldom.parseString(ret.text)
        collection = dom_tree.documentElement
        data = ['err_code', 'return_msg']
        result_data = xmldom_parsing.xmldom(collection, data)
        err_code = result_data.get('err_code')
        return_msg = result_data.get('return_msg')
        print('return_msg----------> ', err_code, return_msg)

        if err_code == 'SUCCESS' and return_msg == '发放成功':
            err_code = 200
            return_msg = '提现成功'

        else:
            if err_code == 'NOTENOUGH': # 账户余额不足
                user_data = get_ent_info(user_id=user_id)
                gongzhonghao_objs = WeChatApi(user_data)
                openid_list = [
                    'oX0xv1iqlzEtIhkeutd6f_wzAEpM', # 赵欣鹏
                    'oX0xv1pmPrR24l6ezv4mI9HE0-ME', # 小明
                    'oX0xv1spo1WyEtg9Exmg7-KXCD3U', # 李娜
                ]
                for i in openid_list:
                    send_msg_template = {
                            "touser": i,
                            "template_id": "09KYbzAOFJsuXUK27G-_3n4OZQjCsiP-Vfe4rSeLIi8",
                            "data": {
                                "first": {
                                    "value": "天眼提现余额不足任务提醒!",
                                    "color": "#173177"
                                },
                                "keyword1": {
                                    "value": "微商天眼余额不足",
                                    "color": "#173177"
                                },
                                "keyword2": {
                                    "value": '充值',
                                    "color": "#173177"
                                },
                                "keyword3": {
                                    "value": now_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                                    "color": "#173177"
                                },
                                "keyword4": {
                                    "value": "北京/通州",
                                    "color": "#173177"
                                },
                                "keyword5": {
                                    "value": "\n用户ID:{}, \n用户名称:{}, \n提现金额:{}元, \n用户余额:{}".format(
                                        user_id, user_name, withdrawal_amount, make_money
                                    ),
                                    "color": "#173177"
                                },
                                "remark": {
                                    "value": "\n{}".format(return_msg),
                                    "color": "#173177"
                                }
                            }
                    }
                    gongzhonghao_objs.sendTempMsg(send_msg_template)

                return_msg = '余额不足,已通知管理员,请稍后重试'

            elif err_code == 'NO_AUTH': # 用户自身账号异常
                return_msg = '微信帐号异常, 请使用常用的活跃的微信号'

            elif err_code == 'MONEY_LIMIT':  # 每个红包金额必须在默认额度内（默认大于1元，小于200元，可在产品设置中自行申请调高额度）
                return_msg = '最低提取额度1元, 最多提取额度200元'

            elif err_code == 'SENDNUM_LIMIT':
                return_msg = '用户每日最多提取次数10次'

            else:
                return_msg = '网络异常, 请稍后重试'

        data = {
            'code': err_code,
            'return_msg': return_msg
        }
        return data














