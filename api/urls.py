
from django.conf.urls import url


from api.views_dir import user, wechat, classify, article, posters, customer, small_shop, brand, team, goods_classify, \
    upload_file, renewal, prepaidManagement, day_eye, letter_operation


urlpatterns = [

    # 分类管理
    # url(r'^classify/(?P<oper_type>\w+)/(?P<o_id>\d+)', classify.classify_oper),
    url(r'^classify$', classify.classify),

    # 公司管理
    # url(r'^company/(?P<oper_type>\w+)/(?P<o_id>\d+)', company.company_oper),
    # url(r'^company', company.company),

    # 文章管理
    url(r'^article/(?P<oper_type>\w+)/(?P<o_id>\d+)', article.article_oper),
    url(r'^article$', article.article),

    # 客户操作文章
    url(r'^article_customer/(?P<oper_type>\w+)$', article.article_customer_oper),


    # 用户管理
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)$', user.user_oper),
    url(r'^user$', user.user),
    url(r'^user_login/(?P<oper_type>\w+)$', user.user_login_oper), # 用户登录

    # 团队管理
    url(r'^team/(?P<oper_type>\w+)/(?P<o_id>\d+)', team.team_oper),
    url(r'^team', team.team),

    # 海报管理
    url(r'^posters/(?P<oper_type>\w+)/(?P<o_id>\d+)', posters.posters_oper),
    url(r'^posters', posters.posters),

    # 客户管理  用户的用户称为客户
    url(r'^customer$', customer.customer),
    url(r'^customer/(?P<oper_type>\w+)/(?P<o_id>\d+)$', customer.customer_oper),

    # 品牌管理
    url(r'^brand/(?P<oper_type>\w+)/(?P<o_id>\d+)', brand.brand_oper),
    url(r'^brand', brand.brand),

    # --------------------------------微店----------------------# 微店分类
    url(r'^goods_classify/(?P<oper_type>\w+)/(?P<o_id>\d+)', goods_classify.goods_classify_oper),
    url(r'^goods_classify', goods_classify.goods_classify),

    # 微店管理
    url(r'^small_shop/(?P<oper_type>\w+)/(?P<o_id>\d+)', small_shop.small_shop_oper),
    url(r'^small_shop', small_shop.small_shop),

    # ---------------------------------图片上传---------------------------------
    url(r'^upload_shard$', upload_file.upload_shard),     # 分片
    url(r'^merge$', upload_file.merge),                   # 合并
    url(r'^upload_base_shard$', upload_file.upload_base_shard),                  # base64 上传分片
    url(r'^base_merge', upload_file.base_merge),                                 # base64 合并

    # # 订单管理
    # url(r'^small_shop/(?P<oper_type>\w+)/(?P<o_id>\d+)', small_shop.small_shop_oper),
    # url(r'^small_shop', small_shop.small_shop),

    # # 退款管理
    # url(r'^small_shop/(?P<oper_type>\w+)/(?P<o_id>\d+)', small_shop.small_shop_oper),
    # url(r'^small_shop', small_shop.small_shop)s,

    # ---------------- 公众号操作 ----------------
    url(r'^wechat/(?P<oper_type>\w+)$', wechat.wechat_oper),
    url(r'^wechat$', wechat.wechat),     # 接受微信服务器发送的请求
    url(r'^share_article/(?P<oper_type>\w+)$', wechat.share_article),     # 客户打开 用户分享的文章
    # url(r'^weichat_generate_qrcode$', wechat.weichat_generate_qrcode),    # 微信获取带参数的二维码

    # ----------------续费管理---------------------
    url(r'^renewal/(?P<oper_type>\w+)/(?P<o_id>\d+)$', renewal.renewal_oper),
    url(r'^renewal$', renewal.renewal),

    # ----------------支付管理--------------------
    url(r'^weixin_pay/(?P<oper_type>\w+)/(?P<o_id>\d+)$', prepaidManagement.weixin_pay),

    # ----------------天眼---------------------
    url(r'^day_eye/(?P<oper_type>\w+)/(?P<o_id>\d+)$', day_eye.day_eye_oper),
    url(r'^day_eye$', day_eye.day_eye),

    # ----------------转发朋友圈等(微信操作)-----------
    url(r'^letter_operation/(?P<oper_type>\w+)$', letter_operation.letter_operation),

]
