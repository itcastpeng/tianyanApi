
from api import models
from urllib.parse import unquote,quote
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
from publicFunc.article_oper import get_ent_info


# 分享 (文章/宝贝) 创建跳转链接
def forwarding_article(pub, user_id=None, inviter_user_id=None, redirect_uri=None):
    print('-********************************************-------------> ', user_id, inviter_user_id)
    if redirect_uri:
        redirect_uri = redirect_uri
    else:  # 文章&微店链接  通用
        redirect_uri = "http://zhugeleida.zhugeyingxiao.com/tianyan/api/share_article/" + str(pub)
    if inviter_user_id:
        user_id = inviter_user_id
    print('user_id--------------------------user_id-------------------user_id-------------> ', user_id)
    data = get_ent_info(user_id)
    weichat_api_obj = WeChatApi(data)

    open_weixin_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope={scope}&state={user_id}#wechat_redirect" \
        .format(
        scope='snsapi_userinfo',
        appid=weichat_api_obj.APPID,
        redirect_uri=redirect_uri,
        user_id=user_id
    )
    # print('open_weixin_url================> ', open_weixin_url)
    open_weixin_uri = quote(open_weixin_url, 'utf-8')
    open_weixin_url = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/wechat/redirect_url?share_url=%s' % open_weixin_uri
    return open_weixin_url













