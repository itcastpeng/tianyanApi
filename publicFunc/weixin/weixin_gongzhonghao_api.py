#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:zhangcong
# Email:zc_92@sina.com

# 微信公众号

import requests
import json
import time
import os
# import sys
# import datetime
import hashlib
# from publicFunc.weixin.weixin_pay_api import weixin_pay_api
from publicFunc.weixin.weixin_api_public import WeixinApiPublic
from api import models
import datetime


# 验证收到的消息是否来自微信服务器
def checkSignature(timestamp, nonce, signature):
    """
    参考微信开发文档 https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421135319
    :param timestamp:
    :param nonce:
    :param signature:
    :return:
    """
    token = 'hfdjsahjklfdhjklhfdkljsa'

    tmp_str = "".join(sorted([timestamp, nonce, token]))
    hash_obj = hashlib.sha1()
    hash_obj.update(tmp_str.encode('utf-8'))
    if hash_obj.hexdigest() == signature:
        return True
    else:
        return False



class WeChatApi(WeixinApiPublic):

    def __init__(self, data):
        self.id = data["id"]
        self.APPID = data["APPID"]
        self.APPSECRET = data["APPSECRET"]
        self.access_token = data.get("access_token")
        create_datetime = data.get("create_datetime")
        if not create_datetime:
            create_datetime = 0
        create_datetime = int(create_datetime)
        self.create_datetime = create_datetime
        if not self.create_datetime or (int(time.time()) - self.create_datetime) > 5000:
            self.get_access_token()

        # if wechat_data_path:
        #     self.wechat_data_path = wechat_data_path
        # else:
        #     self.wechat_data_path = os.path.join(os.getcwd(), "publicFunc", "weixin", "wechat_data.json")
        #
        # # print(wechat_data_path)
        # with open(self.wechat_data_path, "r", encoding="utf8") as f:
        #     data = json.loads(f.read())
        #
        #     self.APPID = data["APPID"]
        #     self.APPSECRET = data["APPSECRET"]
        #     self.access_token = data["access_token"]
        #     self.create_datetime = data["create_datetime"]
        #
        #     # 如果access_token快要过期，则更新access_token，默认过期时间为7200秒
        #     if not self.create_datetime or (int(time.time()) - self.create_datetime) > 7000:
        #         # print(type(self.create_datetime), self.create_datetime)
        #         # print(time.time())
        #         # print((int(time.time()) - self.create_datetime))
        #
        #         self.get_access_token()

        # self.get_users()

    # 获取access_token
    def get_access_token(self):
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}".format(
            APPID=self.APPID,
            APPSECRET=self.APPSECRET
        )
        print("-" * 30 + "获取 access_token" + "-" * 30, url)
        ret = requests.get(url)
        print('ret.text===--------======--------------> ', ret.text)
        self.access_token = json.loads(ret.text)["access_token"]
        print(self.access_token)

        data = {
            "appid": self.APPID,
            "appsecret": self.APPSECRET,
            "access_token": self.access_token,
            "create_datetime": int(time.time())
        }
        # print(data)
        # with open(self.wechat_data_path, "w", encoding="utf8") as f:
        #     f.write(json.dumps(data))
        objs = models.Enterprise.objects.filter(id=self.id)
        objs.update(**data)
        self.access_token = objs[0].access_token
        print("\n" * 3)


    # 获取所有用户的 openid
    def get_users(self):
        print("-" * 30 + "获取用户 openid" + "-" * 30)
        url = "https://api.weixin.qq.com/cgi-bin/user/get?access_token={ACCESS_TOKEN}".format(
            ACCESS_TOKEN=self.access_token
        )
        ret = requests.get(url)

        print(ret.text)

        ret_json = json.loads(ret.text)
        if "errcode" in ret_json and ret_json["errcode"] == 40001:
            self.get_access_token()

        print("\n" * 3)

    # 生成二维码
    def generate_qrcode(self, scene_dict):
        """
        :param scene_dict: 微信将该字典中的值传递给对应的url
        :return:
        """
        print("-" * 30 + "生成二维码" + "-" * 30)
        url = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token={access_token}".format(
            access_token=self.access_token
        )
        post_data = {
            "expire_seconds": 2592000,  # 二维码过期时间 30天 S
            "action_name": "QR_STR_SCENE",
            "action_info": {
                "scene": {
                    "scene_str": json.dumps(scene_dict)
                }
            }
        }

        ret = requests.post(url, data=json.dumps(post_data))
        print(ret.text)
        print(json.loads(ret.text))

        ticket = json.loads(ret.text)["ticket"]

        url = "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket={TICKET}".format(
            TICKET=ticket
        )
        print("\n" * 3)
        return url
        # ret = requests.get(url)
        # print(ret.text)

    # 发送模板消息
    def sendTempMsg(self, post_data):
        url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={ACCESS_TOKEN}".format(
            ACCESS_TOKEN=self.access_token
        )

        # post_data = {
        #     "touser": "o7Xw_0YmQrxqcYsRhFR2y7yQPBMU",
        #     "template_id": "REblvLGT0dVxwzyrp28mBaXKF6XnHhP2_b7hXjUyI2A",
        #     "url": "http://wenda.zhugeyingxiao.com/",
        #     "data": {
        #         "first": {
        #             "value": "问答任务异常！",
        #             "color": "#173177"
        #         },
        #         # "keyword1": {
        #         #     "value": "修改问答任务",
        #         #     "color": "#173177"
        #         # },
        #         "keyword2": {
        #             "value": datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"),
        #             "color": "#173177"
        #         },
        #         # "keyword3": {
        #         #     "value": "发布失败",
        #         #     "color": "#173177"
        #         # },
        #         # "keyword4": {
        #         #     "value": "请修改",
        #         #     "color": "#173177"
        #         # },
        #         "remark": {
        #             "value": "问题:嘻嘻嘻\n答案:嘻嘻嘻",
        #             "color": "#173177"
        #         }
        #     }
        # }

        ret = requests.post(url, data=json.dumps(post_data))
        print(ret.text)

    # 创建菜单
    def createMenu(self, menu_data):
        url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token={ACCESS_TOKEN}".format(
            ACCESS_TOKEN=self.access_token
        )
        # post_data = {
        #     "button": [
        #         {
        #             "name": "诸葛问答",
        #             "sub_button": [
        #                 {
        #                     "type": "view",
        #                     "name": "查看诸葛问答效果",
        #                     "url": "http://www.bjhzkq.com",
        #                 }
        #             ]
        #         }
        #     ]
        # }

        # print(parse.urlencode())
        post_data_json = json.dumps(menu_data, ensure_ascii=False).encode('utf8')
        print(post_data_json)
        ret = requests.post(url, data=post_data_json)

        print(ret.text)

    # 删除菜单
    def deleteMenu(self):
        url = 'https://api.weixin.qq.com/cgi-bin/menu/delete?access_token={access_token}'.format(
            access_token=self.access_token
        )
        ret= requests.get(url)
        print(ret.text)

    # 创建个性化菜单
    def createCustomMenu(self, menu_data):
        url = "https://api.weixin.qq.com/cgi-bin/menu/addconditional?access_token={ACCESS_TOKEN}".format(
            ACCESS_TOKEN=self.access_token
        )

        post_data_json = json.dumps(menu_data, ensure_ascii=False).encode()
        print(post_data_json)
        ret = requests.post(url, data=post_data_json)

        # print(ret.text)

    # 删除自定义菜单
    def delMenu(self):
        print("=" * 50 + "删除自定义菜单" + "=" * 50)
        url = "https://api.weixin.qq.com/cgi-bin/menu/exct_delete?access_token={ACCESS_TOKEN}".format(
            ACCESS_TOKEN=self.access_token
        )

        ret = requests.get(url)
        # print(ret.text)

    # 获取自定义菜单
    def getMenu(self):
        url = "https://api.weixin.qq.com/cgi-bin/menu/get?access_token={ACCESS_TOKEN}".format(
            ACCESS_TOKEN=self.access_token
        )
        ret = requests.get(url)
        print('获取自定义菜单ret.text-----> ', ret.text)

    # 创建标签
    def create_tag(self, tag_name):
        url = "https://api.weixin.qq.com/cgi-bin/tags/create?access_token={ACCESS_TOKEN}".format(
            ACCESS_TOKEN=self.access_token
        )

        post_data = {
            "tag": {"name": tag_name}
        }

        ret = requests.post(url, data=json.dumps(post_data, ensure_ascii=False).encode())
        return ret.text

    # 查看已经创建的所有标签
    def get_tags(self):
        url = "https://api.weixin.qq.com/cgi-bin/tags/get?access_token={ACCESS_TOKEN}".format(
            ACCESS_TOKEN=self.access_token
        )
        ret = requests.get(url)
        return ret.text

    # 给用户关联标签
    def batch_tagging(self, openid, tag_id):
        """
        :param openid:  用户公众号的id
        :param tag_id:  公众号标签的id
        :return:
        """
        # print("给用户关联标签")
        url = "https://api.weixin.qq.com/cgi-bin/tags/members/batchtagging?access_token={ACCESS_TOKEN}".format(
            ACCESS_TOKEN=self.access_token
        )

        post_data = {
            "openid_list": [
                openid
            ],
            "tagid": tag_id
        }
        # print("post_data -->", post_data)

        ret = requests.post(url, data=json.dumps(post_data, ensure_ascii=False).encode())
        print(ret.text)

    # 获取用户基本信息
    def get_user_info(self, openid):
        url = "https://api.weixin.qq.com/cgi-bin/user/info?access_token={ACCESS_TOKEN}&openid={OPENID}&lang=zh_CN".format(
            ACCESS_TOKEN=self.access_token,
            OPENID=openid
        )
        ret = requests.get(url)
        return ret.json()

    # 获取jsapi_ticket 签名算法用
    def get_jsapi_ticket(self):
        # print('self.access_token-----------------> ', self.access_token)
        url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={}&type=jsapi'.format(self.access_token)
        ret = requests.get(url)

        return str(ret.json().get('ticket'))

    # 获取signature
    def get_signature(self):

        timestamp = int(time.time())
        noncestr = self.generateRandomStamping()
        ticket = self.get_jsapi_ticket()

        result_data = {
            'noncestr': noncestr,   # 随机值32位
            'jsapi_ticket': ticket,
            'timestamp': timestamp,
            'url': 'http://zhugeleida.zhugeyingxiao.com/tianyan/'
            # 'url': 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/wechat'
            # 'url': 'http://tianyan.zhangcong.top/api/letter_operation/js_sdk_permissions'

        }

        # result_data = {
        #     "noncestr": "Wm3WZYTPz0wzccnW",
        #     "jsapi_ticket": "sM4AOVdWfPE4DxkXGEs8VMCPGGVi4C3VM0P37wVUCFvkVAy_90u5h9nbSlYy3-Sl-HhTdfl2fzFy1AOcHKP7qg",
        #     "timestamp": "1414587457",
        #     "url": "http://mp.weixin.qq.com?params=value",
        # }

        # print('result_data---> ', result_data)
        str1 = self.shengchengsign(result_data)
        # print('str1--------> ', str1)
        signature = self.sha1(str1)
        # print('signature---------> ', signature)
        data = {
            'signature': signature,
            'timestamp': timestamp,
            'noncestr': noncestr,
            'appid': self.APPID,
        }
        return data


    # 通过 code 获取openid/用户信息（公众号）
    def get_openid(self, code):
        print('self.APPID, self.APPSECRET===========> ', self.APPID, self.APPSECRET)
        url = "https://api.weixin.qq.com/sns/oauth2/access_token?" \
              "appid={APPID}&secret={SECRET}&code={CODE}&grant_type=authorization_code" \
            .format(
            APPID=self.APPID,
            SECRET=self.APPSECRET,
            CODE=code,
        )
        print('-----------开始请求第一个链接--------------------', datetime.datetime.today())
        ret = requests.get(url)
        print('-----------结束请求第一个链接--------------------', datetime.datetime.today())
        ret.encoding = "utf8"
        print("ret.text -->", ret.text)

        access_token = ret.json().get('access_token')
        openid = ret.json().get('openid')
        print('access_token, openid--------。 ', access_token, openid)
        url = "https://api.weixin.qq.com/sns/userinfo?access_token=" \
              "{ACCESS_TOKEN}&openid={OPENID}&lang=zh_CN" \
            .format(
            ACCESS_TOKEN=access_token,
            OPENID=openid,
        )
        print('-----------开始请求第二个链接--------------------', datetime.datetime.today())
        ret = requests.get(url)
        print('-----------结束请求第二个链接--------------------', datetime.datetime.today())
        ret.encoding = "utf8"
        ret_obj = ret.json()
        print('ret_obj---------------> ', ret_obj)
        data = {
            'openid':openid,
            'sex':ret_obj.get('sex'),
            'country':ret_obj.get('country'),
            'city':ret_obj.get('city'),
            'province':ret_obj.get('province'),
            'nickname':ret_obj.get('nickname'),
            'subscribe':ret_obj.get('subscribe'),
            'headimgurl':ret_obj.get('headimgurl'),
        }

        return data


    # 客服消息
    def  news_service(self, data):
        url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={}'.format(self.access_token)
        ret = requests.post(url, data=data)
        print('ret.text--客服消息--------->', ret.text)



# if __name__ == '__main__':
#
#     obj = WeChatApi("wechat_data.json")
#     obj.get_jsapi_ticket()
