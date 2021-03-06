from api import models
from publicFunc import Response
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.customer import SelectForm
import json, requests

# cerf  token验证 用户展示模块
# @account.is_token(models.Userprofile)
def customer(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'name': '__contains',
                'create_datetime': '',
                'sex': '',
            }

            q = conditionCom(request, field_dict)

            print('q -->', q)
            objs = models.Customer.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:

                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,
                    'phone_number': obj.phone_number,
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
                'name': "姓名",
                'phone_number': "手机号",
            }
        else:
            print("forms_obj.errors -->", forms_obj.errors)
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


# 增删改
# token验证
# @account.is_token(models.Userprofile)
def customer_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    # user_id = request.GET.get('user_id')
    print('request.POST -->', request.POST)
    if request.method == "GET":
        if oper_type == "add_customer":

            pass
    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)





















