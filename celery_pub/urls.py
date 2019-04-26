
from django.conf.urls import url


from api.views_dir import user, wechat, classify, article, posters, customer, small_shop, brand, team, goods_classify, \
    upload_file, renewal, prepaidManagement, day_eye, letter_operation, platform_add_article, html_oper, qiniu_oper


urlpatterns = [

    # 平台加入文章
    url(r'^platform_add_article/(?P<oper_type>\w+)', platform_add_article.article_oper),

]
