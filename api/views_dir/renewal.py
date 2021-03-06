from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.renewal import  SelectForm
from publicFunc.base64_encryption import b64decode
import json


# cerf  token验证 用户展示模块
@account.is_token(models.Userprofile)
def renewal(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            user_id = request.GET.get('user_id')
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_date')
            field_dict = {
                'id': '',
                'price': '__contains',
                'the_length': '',
                'renewal_number_days': '',
                'create_date': '',
                'create_user_id': '',
            }
            user_obj = models.Userprofile.objects.get(id=user_id)
            q = conditionCom(request, field_dict)



            print('q -->', q)
            objs = models.renewal_management.objects.filter(
                q,
                create_user_id=user_obj.enterprise_id
            ).order_by(order)
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
                    'price': obj.price,
                    'original_price': obj.original_price,
                    'the_length_id': obj.the_length,
                    'the_length': obj.get_the_length_display(),
                    'create_user_id': obj.create_user_id,
                    'create_user__name': b64decode(obj.create_user.name),
                    'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S')
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }
            response.note = {
                'id': "id",
                'price': '钱数',
                'the_length_id': '时长ID(一个月， 一年....)',
                'the_length': '时长',
                'create_user_id': '创建人ID',
                'create_user__name': '创建人名字',
                'original_price': '原价',
                'create_date': '创建时间',
            }
        else:
            print("forms_obj.errors -->", forms_obj.errors)
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)



