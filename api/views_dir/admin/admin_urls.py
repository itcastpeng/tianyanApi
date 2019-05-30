from django.conf.urls import url
from api.views_dir.admin import login, admin_user

urlpatterns = [
    # 账号密码登录
    url(r'^login$', login.login),

    # 后台用户管理
    url(r'^user/(?P<oper_type>\w+)/(?P<o_id>\d+)$', admin_user.user_oper),
    url(r'^user$', admin_user.user),
    url(r'^update_pwd$', admin_user.updatePwd),







    ]