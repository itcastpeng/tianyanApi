from django.conf.urls import url
from api.views_dir.admin import login, admin_user, renewal

urlpatterns = [
    # 账号密码登录
    url(r'^login$', login.login),

    # 首页数据
    url(r'^index/(?P<oper_type>\w+)$', login.index_info),

    # 后台用户管理
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)$', admin_user.user_oper),
    url(r'^user$', admin_user.user),
    url(r'^update_pwd$', admin_user.updatePwd),

    # 续费管理
    url(r'^renewal/(?P<oper_type>\w+)/(?P<o_id>\d+)$', renewal.renewal_oper),
    url(r'^renewal$', renewal.renewal),






    ]