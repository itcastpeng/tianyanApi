

from urllib.parse import unquote,quote
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi



# 分享文章 创建跳转链接
def forwarding_article(article_id, user_id=None, inviter_user_id=None):
    weichat_api_obj = WeChatApi()

    redirect_uri = "http://zhugeleida.zhugeyingxiao.com/tianyan/api/share_article/" + 'article_' + str(article_id)
    if inviter_user_id:
        user_id = inviter_user_id
    open_weixin_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope={scope}&state={user_id}#wechat_redirect" \
        .format(
        scope='snsapi_userinfo',
        appid=weichat_api_obj.APPID,
        redirect_uri=redirect_uri,
        user_id=user_id
    )
    redirect_url = quote(open_weixin_url, 'utf-8')
    open_weixin_url = 'http://zhugeleida.zhugeyingxiao.com/tianyan/api/wechat/redirect_url?share_url=%s' % redirect_url
    return open_weixin_url

# 分享微店宝贝 创建跳转链接
def share_micro_store(micro_store_baby, user_id=None, inviter_user_id=None):
    weichat_api_obj = WeChatApi()
    redirect_uri = "http://zhugeleida.zhugeyingxiao.com/tianyan/api/share_article/" + 'micro_' + str(micro_store_baby)

    if inviter_user_id:
        user_id = inviter_user_id
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













