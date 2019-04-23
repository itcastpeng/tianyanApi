from django.shortcuts import HttpResponse
from django.http import JsonResponse
from api import models
from publicFunc.account import get_token
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
from publicFunc import Response
from publicFunc import base64_encryption
from publicFunc.forwarding_article import forwarding_article
from django.shortcuts import render, redirect
from publicFunc.weixin import weixin_gongzhonghao_api
from publicFunc.base64_encryption import b64decode, b64encode
from publicFunc.host import host_url
from publicFunc.article_oper import get_ent_info
from publicFunc.weixin.weixin_gongzhonghao_api import checkSignature
from publicFunc.article_oper import get_ent_info
from publicFunc.get_content_article import get_article
from publicFunc.article_oper import add_article_public
from publicFunc.account import str_encrypt
import json, xml.dom.minidom, datetime, time, requests



# 创建或更新用户信息
def updateUserInfo(openid, inviter_user_id, ret_obj):
    """
    :param openid:  微信openid
    :param inviter_user_id: 邀请人id
    :param ret_obj:  微信数据
    :return:
    """
    print('ret_obj -->', ret_obj)
    """
        {
            'subscribe_scene': 'ADD_SCENE_QR_CODE',
            'city': '丰台',
            'openid': 'oX0xv1pJPEv1nnhswmSxr0VyolLE',
            'qr_scene': 0,
            'tagid_list': [],
            'nickname': '张聪',
            'subscribe_time': 1527689396,
            'country': '中国',
            'groupid': 0,
            'subscribe': 1,
            'qr_scene_str': '{"timestamp": "1527689369548"}',
            'headimgurl': 'http://thirdwx.qlogo.cn/mmopen/oFswpUmYn53kTv5QdmmONicVJqp3okrhHospu6icoLF7Slc5XyZWR
                            96STN9RiakoBQn1uoFJIWEicJgJ1QjR5iaGOgWNQ5BSVqFe5/132',
            'province': '北京',
            'sex': 1,
            'language': 'zh_CN',
            'remark': ''
        }


        {
            "openid":"oX0xv1pJPEv1nnhswmSxr0VyolLE",
            "nickname":"张聪",
            "sex":1,
            "language":"zh_CN",
            "city":"丰台",
            "province":"北京",
            "country":"中国",
            "headimgurl":"http://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTJWGnNTvluYlHj8qt8HnxMlwbRiad
                            bv4TNrp4watI2ibPPAp2Hu6Sm1BqYf6IicNWsSrUyaYjIoy2Luw/132",
            "privilege":[]
        }
    """
    # 保证1个微信只能够关联1个账号
    user_objs = models.Userprofile.objects.filter(openid=openid)

    encode_username = base64_encryption.b64encode(ret_obj['nickname'])
    user_data = {
        "sex": ret_obj.get('sex'),
        "country": ret_obj.get('country'),
        "province": ret_obj.get('province'),
        "city": ret_obj.get('city'),
        "headimgurl": ret_obj.get('headimgurl'),
        "wechat_name": encode_username,
    }

    if user_objs:
        user_id = user_objs[0].id
        user_objs.update(**user_data)
    else:
        # encodestr = base64.b64encode(ret_obj['nickname'].encode('utf8'))
        # encode_username = str(encodestr, encoding='utf8')
        overdue_date = datetime.datetime.now() + datetime.timedelta(days=30)

        subscribe = ret_obj.get('subscribe')

        # 如果没有关注，获取个人信息判断是否关注
        if not subscribe:
            data = get_ent_info(inviter_user_id)
            weichat_api_obj = WeChatApi(data)
            ret_obj = weichat_api_obj.get_user_info(openid=openid)
            subscribe = ret_obj.get('subscribe')

        user_data['wechat_name'] = encode_username
        user_data['headimgurl'] = ret_obj.get('headimgurl')
        user_data['inviter_id'] = inviter_user_id
        user_data['set_avator'] = ret_obj.get('headimgurl')
        user_data['subscribe'] = subscribe
        user_data['name'] = encode_username
        user_data['openid'] = ret_obj.get('openid')
        user_data['overdue_date'] = overdue_date
        user_data['token'] = get_token()
        print("user_data --->", user_data)
        user_obj = models.Userprofile.objects.create(**user_data)
        user_id = user_obj.id
    return user_id


# 有人(关注/取关)公众号 微信服务器调用的接口
def wechat(request):
    signature = request.GET.get("signature")
    timestamp = request.GET.get("timestamp")
    nonce = request.GET.get("nonce")
    echostr = request.GET.get("echostr")

    # 该值做消息解密使用，当前未使用加密模式，参考微信开发文档 https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421135319
    # EncodingAESKey = 'LFYzOBp42g5kwgSUWhGC9uRugSmpyetKfAsJa5FdFHX'

    check_result = checkSignature(timestamp, nonce, signature)
    print('check_result -->', check_result)

    if check_result:

        if request.method == "GET":
            return HttpResponse(echostr)
        else:
            body_text = str(request.body, encoding="utf8")
            print('body_text -->', body_text)

            # 使用minidom解析器打开 XML 文档
            DOMTree = xml.dom.minidom.parseString(body_text)
            collection = DOMTree.documentElement

            # 事件类型
            msg_type = collection.getElementsByTagName("MsgType")[0].childNodes[0].data

            # 用户的 openid
            openid = collection.getElementsByTagName("FromUserName")[0].childNodes[0].data

            # 事件类型 关注/取关
            if msg_type == 'event':
                event = collection.getElementsByTagName("Event")[0].childNodes[0].data
                # 扫描带参数的二维码
                if event in ["subscribe", "SCAN"]:
                    # subscribe = 首次关注
                    # SCAN = 已关注
                    # 事件 Key 值
                    inviter_user_id = ''
                    if collection.getElementsByTagName("EventKey")[0].childNodes:
                        event_key = collection.getElementsByTagName("EventKey")[0].childNodes[0].data
                        if event == "subscribe":
                            event_key = event_key.split("qrscene_")[-1]
                        event_key = json.loads(event_key)
                        inviter_user_id = event_key.get('inviter_user_id')      # 邀请人id
                        print('event_key -->', event_key)

                    data = get_ent_info(inviter_user_id) # 获取该用户 token appid等
                    weichat_api_obj = WeChatApi(data)
                    ret_obj = weichat_api_obj.get_user_info(openid=openid)
                    updateUserInfo(openid, inviter_user_id, ret_obj)

                    if event == 'subscribe':  # 首次关注
                        nickname = ret_obj.get('nickname')  # 关注人名称
                        post_data = {
                            "touser": openid,
                            "template_id": "gwB4lxYzpWhtyFSFs3Pj0ZrMweHY0-GCTvS4b0ZeTmI",  # 登录提醒模板
                            # "url": "http://wenda.zhugeyingxiao.com/",
                            "data": {
                                "first": {
                                    "value": "欢迎关注微商天眼公众号!",
                                    "color": "#173177"
                                },
                                "keyword1": {
                                    "value": nickname,
                                    "color": "#173177"
                                },
                                "keyword2": {
                                    "value": datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"),
                                    "color": "#173177"
                                },
                                "remark": {
                                    "value": "感谢使用,请注意账号安全!\n进入天眼请点击最下方↓↓↓",
                                    "color": "#173177"
                                }
                            }
                        }
                        weichat_api_obj.sendTempMsg(post_data)

                # 取消关注
                elif event == "unsubscribe":
                    print('-------------取关')
                    # models.Userprofile.objects.filter(openid=openid).update(openid=None)
                    # we_chat_public_send_msg_obj.sendTempMsg(post_data)

            elif msg_type == 'text':
                print('---------用户发送消息')
                Content = collection.getElementsByTagName("Content")[0].childNodes[0].data
                user_obj = models.Userprofile.objects.get(openid=openid)  # 获取用户ID
                if 'http' in Content:  # 获取文章内容 返回文章
                    print('Content=-===========》', Content)
                    data_dict = get_article(Content)    # 获取文章
                    id = add_article_public(data_dict, 39)  # 创建文章 第二个参数为 classify_id 默认为其他
                    url = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/wechat/forwarding_article?article_id={}&user_id={}'.format(
                        id,
                        user_obj.id
                    )
                    print('url-----> ', url)

                else: # 收到其他文字 发送随机五篇文章
                    timestamp = str(int(time.time()))
                    rand_str = str_encrypt(timestamp + user_obj.token)
                    share_url = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/article/popula_articles/0?length=5&rand_str={}&timestamp={}&user_id={}'.format(
                        rand_str,
                        timestamp,
                        user_obj.id,
                    )
                    ret = requests.get(share_url)
                    print('share_url-------> ', share_url)
                    print('ret.text-------> ', ret.text)
                    ret.encoding = 'utf8'
                    ret_json = ret.json().get('data')
                    print('ret_json--------> ', ret_json)
                    content = ''
                    for i in ret_json.get('ret_data'):
                        url = 'http://zhugeleida.zhugeyingxiao.com/tianyan/#/Article/Article_Detail?id={}&token={}&user_id={}%classify_type=1'.format(
                            i.get('id'),
                            user_obj.token,
                            user_obj.id
                        )
                        pinjie_content = '{}<a href="{url}">{title}</a>'.format(
                            b64decode('4p6h'),  # emoji解码  →箭头
                            title=i.get('title'),
                            url=url
                        )
                        content += ' \n{} \n'.format(pinjie_content)

                    post_data = {
                        "touser":openid,
                        "msgtype": "text",
                        "text": {
                            "content":'天眼将一直为您推送消息 \n{} \n点击下方天眼,更多内容等你哦!'.format(
                                content
                            )
                        }
                    }
                    post_data = bytes(json.dumps(post_data, ensure_ascii=False), encoding='utf-8')
                    print('post_data--------> ', post_data)

                    data = get_ent_info(user_obj.id)  # 获取该用户appid等
                    weichat_api_obj = WeChatApi(data)  # 实例化公众号操作
                    weichat_api_obj.news_service(post_data)

            return HttpResponse("")

    else:
        return HttpResponse(False)







# @account.is_token(models.Userprofile)
def wechat_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":
        pass

    else:
        # 获取用于登录的微信二维码
        data = get_ent_info(user_id)
        weichat_api_obj = WeChatApi(data)
        # 推广赚钱 生成二维码
        # if oper_type == "generate_qrcode":


        # 邀请成员页面展示信息
        if oper_type == "invite_members":
            print('request.GET=====invite_members------------invite_members------------invite_members====', request.GET)
            team_id = request.GET.get('team_id')
            inviter_user_id = request.GET.get('inviter_user_id') # 用户ID

            redirect_uri = '{host_url}api/invite_members/invitation_page/{o_id}'.format(
                host_url=host_url,
                o_id=team_id,  # 团队ID
            )

            if inviter_user_id:  # 多次转发
                redirect_url = forwarding_article(pub=1, redirect_uri=redirect_uri, inviter_user_id=inviter_user_id)
                user_id = inviter_user_id

            else: # 首次转发
                # 第一次链接 接收邀请页面
                redirect_url = forwarding_article(pub=1, redirect_uri=redirect_uri, user_id=user_id)

            obj = models.UserprofileTeam.objects.select_related('team', 'user').get(team_id=team_id, user_id=user_id)
            team_name = obj.team.name  # 团队名称
            user_name = base64_encryption.b64decode(obj.user.name)  # 客户名称
            set_avator = obj.user.set_avator  # 客户头像
            response.code = 200
            response.data = {
                "open_weixin_url": redirect_url,
                "team_id": team_id,
                "team_name": team_name,
                "user_name": user_name,
                "set_avator":set_avator
            }

            response.note = {
                "open_weixin_url": "分享邀请成员URL",
                "team_name": "团队名称",
                "user_name": "邀请人名称",
                "set_avator": "邀请人头像"
            }

        # 用户分享文章①
        elif oper_type == 'forwarding_article':
            article_id = request.GET.get('article_id')
            inviter_user_id = request.GET.get('inviter_user_id') # 二级以上文章转发 需要传递用户ID
            pub = 'article_' + str(article_id)
            if inviter_user_id:     # 二次转发及以上
                open_weixin_url = forwarding_article(
                    pub=pub,
                    inviter_user_id=inviter_user_id
                )
            else: # 首次转发
                open_weixin_url = forwarding_article(
                    user_id=user_id,
                    pub=pub,
                )
            response.code = 200
            response.msg = '转发成功'
            response.data = {
                'open_weixin_url': open_weixin_url
            }

        # 用户分享微店宝贝①
        elif oper_type == 'share_micro_store':
            micro_store_baby = request.GET.get('micro_store_baby') # 宝贝ID
            inviter_user_id = request.GET.get('inviter_user_id') # 二级以上微店宝贝转发 需要传递用户ID
            pub = 'micro_' + str(micro_store_baby)
            if inviter_user_id:
                open_weixin_url = forwarding_article(
                    inviter_user_id=inviter_user_id,
                    pub=pub,
                )
            else:
                open_weixin_url = forwarding_article(
                    user_id=user_id,
                    pub=pub,
                )
            response.code = 200
            response.msg = '转发成功'
            response.data = {
                'open_weixin_url': open_weixin_url
            }

        # 分享的链接 跳转②
        elif oper_type == 'redirect_url':
            share_url = request.GET.get('share_url')
            redirect_uri = request.GET.get('redirect_uri')
            scope = request.GET.get('scope')
            state = request.GET.get('state')
            response_type = request.GET.get('response_type')

            if redirect_uri:
                redirect_url = str(share_url) + '&redirect_uri=' + str(redirect_uri) + '&response_type=' + str(response_type) + '&scope=' + str(scope) + '&state=' + str(state)
            else:
                redirect_url = share_url
            print('==================跳转链接========================================')
            print('request.GET========> ', request.GET)
            print('redirect_url-------------------> ', redirect_url)
            return redirect(redirect_url)

    return JsonResponse(response.__dict__)





# 客户打开 用户分享的文章 (嵌入微信url 获取用户信息 匹配openid 判断数据库是否存在 跳转文章页)③
def share_article(request, oper_type):
    code = request.GET.get('code')
    code_objs = models.save_code.objects.filter(save_code=code)
    if not code_objs:
        models.save_code.objects.create(save_code=code)
        state = request.GET.get('state')  # 分享文章的用户id
        data = get_ent_info(state)
        weichat_api_obj = weixin_gongzhonghao_api.WeChatApi(data)
        ret_obj = weichat_api_obj.get_openid(code)
        openid = ret_obj.get('openid')
        print('ret_obj-----------> ', ret_obj)
        encode_username = b64encode(
            ret_obj['nickname']
        )
        user_data = {
            "sex": ret_obj.get('sex'),
            "country": ret_obj.get('country'),
            "province": ret_obj.get('province'),
            "city": ret_obj.get('city'),
            'name': encode_username,
            'set_avator': ret_obj.get('headimgurl')
        }
        customer_objs = models.Customer.objects.filter(openid=openid)
        if customer_objs:   # 客户已经存在
            customer_objs.update(**user_data)
            customer_obj = customer_objs[0]
        # 不存在，创建用户
        else:
            subscribe = ret_obj.get('subscribe')

            user_data['set_avator'] = ret_obj.get('headimgurl')
            # 如果没有关注，获取个人信息判断是否关注
            if not subscribe:
                ret_obj_subscribe = weichat_api_obj.get_user_info(openid=openid)
                subscribe = ret_obj_subscribe.get('subscribe')

            print('ret_objret_obj--ret_obj---> ', ret_obj)
            user_data['subscribe'] = subscribe
            user_data['name'] = encode_username
            user_data['openid'] = ret_obj.get('openid')
            user_data['token'] = get_token()
            print("user_data --->", user_data)
            customer_obj = models.Customer.objects.create(**user_data)
        objs = models.Customer.objects.filter(openid=openid)
        obj = objs[0]

        _type = oper_type.split('_')[0]  # 类型
        oid = oper_type.split('_')[1]  # ID
        print('o_id---o_id--o_id--> ', oper_type)
        if _type == 'article':
            # 此处跳转到文章页面 文章
            redirect_url = '{host_url}#/share_article?user_id={user_id}&token={token}&id={article_id}&inviter_user_id={inviter_user_id}'.format(
                host_url=host_url,
                article_id=oid,  # 分享文章的id
                user_id=customer_obj.id,
                token=obj.token,
                inviter_user_id=state,
            )
        elif _type == 'micro':
            # 此处跳转到微店宝贝页面
            redirect_url = '{host_url}#/share_micro_store?user_id={user_id}&token={token}&id={article_id}&inviter_user_id={inviter_user_id}'.format(
                host_url=host_url,
                article_id=oid,  # 分享文章的id
                user_id=customer_obj.id,
                token=obj.token,
                inviter_user_id=state,
            )
        else:
            redirect_url = ''
        return redirect(redirect_url)













# # 获取用于登录的微信二维码
# @account.is_token(models.Userprofile)
# def weichat_generate_qrcode(request):
#     weichat_api_obj = WeChatApi()
#     response = ResponseObj()
#     user_id = request.GET.get('user_id')
#     qc_code_url = weichat_api_obj.generate_qrcode({'inviter_user_id': user_id})
#     print(qc_code_url)
#
#     expire_date = (datetime.datetime.now().date() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
#     response.code = 200
#     response.data = {
#         'qc_code_url': qc_code_url,
#         'expire_date': expire_date
#     }
#
#     return JsonResponse(response.__dict__)


# @csrf_exempt
# def wechat_login(request):
#     response = ResponseObj()
#     timestamp = request.POST.get('timestamp')
#     user_objs = models.zhugedanao_userprofile.objects.select_related('level_name').filter(timestamp=timestamp)
#     if user_objs:
#         user_obj = user_objs[0]
#         response.code = 200
#         decode_username = base64.b64decode(user_obj.username)
#         username = str(decode_username, 'utf-8')
#         role_id = ''
#         if user_obj.role:
#             role_id = user_obj.role.id
#         response.data = {
#             'token': user_obj.token,
#             'user_id': user_obj.id,
#             'set_avator': user_obj.set_avator,
#             'role_id':role_id,
#             'username':username,
#             'level_name': user_obj.level_name.name
#         }
#         response.msg = "登录成功"
#     else:
#         response.code = 405
#         response.msg = '扫码登录异常，请重新扫描'
#
#     return JsonResponse(response.__dict__)
