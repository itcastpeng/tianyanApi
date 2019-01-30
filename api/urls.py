
from django.conf.urls import url

from api.views_dir import user, wechat, classify, article

urlpatterns = [

    # 分类管理
    # url(r'^classify/(?P<oper_type>\w+)/(?P<o_id>\d+)', classify.classify_oper),
    url(r'^classify', classify.classify),

    # # 公司管理
    # url(r'^company/(?P<oper_type>\w+)/(?P<o_id>\d+)', company.company_oper),
    # url(r'^company', company.company),

    # 文章管理
    url(r'^article/(?P<oper_type>\w+)/(?P<o_id>\d+)', article.article_oper),
    url(r'^article', article.article),

    # 用户管理
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user.user_oper),
    url(r'^user', user.user),

    # 文章管理
    url(r'^article/(?P<oper_type>\w+)/(?P<o_id>\d+)', article.article_oper),
    url(r'^article', article.article),

    # ---------------- 公众号操作 ----------------
    url(r'^wechat', wechat.wechat),     # 接受微信服务器发送的请求
    url(r'^weichat_generate_qrcode', wechat.weichat_generate_qrcode)    # 微信获取带参数的二维码

]
