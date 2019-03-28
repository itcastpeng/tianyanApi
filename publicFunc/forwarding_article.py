

from urllib.parse import unquote,quote
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi



# 分享文章 创建跳转链接
def forwarding_article(user_id, article_id):
    weichat_api_obj = WeChatApi()
    redirect_uri = "http://zhugeleida.zhugeyingxiao.com/tianyan/api/share_article/" + article_id
    open_weixin_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope={scope}&state={user_id}#wechat_redirect" \
        .format(
        scope='snsapi_userinfo',
        appid=weichat_api_obj.APPID,
        redirect_uri=redirect_uri,
        user_id=user_id
    )
    redirect_url = quote(open_weixin_url, 'utf-8')
    open_weixin_url = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/redirect_url?share_url=%s' % redirect_url
    return open_weixin_url