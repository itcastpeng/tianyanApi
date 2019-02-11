
from django.conf.urls import url


from api.views_dir import user, wechat, classify, article, posters, customer, small_shop, brand


urlpatterns = [

    # 分类管理
    # url(r'^classify/(?P<oper_type>\w+)/(?P<o_id>\d+)', classify.classify_oper),
    url(r'^classify$', classify.classify),

    # # 公司管理
    # url(r'^company/(?P<oper_type>\w+)/(?P<o_id>\d+)', company.company_oper),
    # url(r'^company', company.company),

    # 文章管理
    url(r'^article/(?P<oper_type>\w+)/(?P<o_id>\d+)', article.article_oper),
    url(r'^article', article.article),

    # 用户管理
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)', user.user_oper),
    url(r'^user', user.user),

    # 海报管理
    url(r'^posters/(?P<oper_type>\w+)/(?P<o_id>\d+)', posters.posters_oper),
    url(r'^posters', posters.posters),

    # 用户管理
    url(r'^customer', customer.customer),

    # 微店管理
    url(r'^small_shop/(?P<oper_type>\w+)/(?P<o_id>\d+)', small_shop.small_shop_oper),
    url(r'^small_shop', small_shop.small_shop),

    # 品牌管理
    url(r'^brand/(?P<oper_type>\w+)/(?P<o_id>\d+)', brand.brand_oper),
    url(r'^brand', brand.brand),

    # ---------------- 公众号操作 ----------------
    url(r'^wechat$', wechat.wechat),     # 接受微信服务器发送的请求
    url(r'^weichat_generate_qrcode$', wechat.weichat_generate_qrcode)    # 微信获取带参数的二维码

]
