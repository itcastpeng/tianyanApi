from django.conf.urls import url
from api.views_dir.admin import login

urlpatterns = [
    # 账号密码登录
    url(r'^login$', login.login),















    ]