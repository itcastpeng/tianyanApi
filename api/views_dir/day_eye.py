from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.day_eye import SelectForm
import json


# cerf  token验证 用户展示模块
# @account.is_token(models.Userprofile)
def day_eye(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
            }

            q = conditionCom(request, field_dict)

            print('q -->', q)
            objs = models.SelectArticleLog.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:
                ret_data.append({
                    'id':obj.id,
                    'customer_id':obj.customer_id,
                    'customer__name':obj.customer.name,
                    'inviter_id':obj.inviter_id,
                    'inviter__name':obj.inviter.name,
                    'article_id':obj.article_id,
                    'article__title':obj.article.title,
                    'close_datetime':obj.close_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'create_datetime':obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                })

            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }
            response.note = {
                'id': "用户id",
                'customer_id': "查看人ID",
                'customer__name': "查看人姓名",
                'inviter_id': "分享人ID",
                'inviter__name': "分享人姓名",
                'article_id': "文章ID",
                'article__title': "文章标题",
                'close_datetime': "关闭页面时间",
                'create_datetime': "创建时间",
            }
        else:
            print("forms_obj.errors -->", forms_obj.errors)
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


# 增删改
# token验证
@account.is_token(models.Userprofile)
def day_eye_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    print('request.POST -->', request.POST)
    if request.method == "POST":
        # 设置推荐分类
        if oper_type == "":
            pass

    else:
        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)
