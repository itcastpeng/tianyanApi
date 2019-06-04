from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from api.forms.admin.renewal import  AddForm, UpdateForm, DeleteForm, SelectForm
from publicFunc.condition_com import conditionCom
from publicFunc.base64_encryption import b64decode

import json


@account.is_token(models.Enterprise)
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
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.renewal_management.objects.filter(
                q,
                create_user_id=user_id
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
                    'create_user__name': obj.create_user.name,
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


@account.is_token(models.Enterprise)
def renewal_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    form_data = {
        'o_id': o_id,
        'user_id': request.GET.get('user_id'),
        'price': request.POST.get('price'),
        'original_price': request.POST.get('original_price'),   # 原价
        'the_length': request.POST.get('the_length')            # 时长ID
    }

    if request.method == "POST":

        # 修改续费
        if oper_type == "update":
            form_obj = UpdateForm(form_data)
            if form_obj.is_valid():
                o_id, objs = form_obj.cleaned_data.get('o_id')
                user_id = request.GET.get('user_id')

                try:
                    obj = models.renewal_management.objects.get(
                        id=o_id,
                        create_user_id=user_id
                    )

                    renewal_log_objs = models.update_renewal_log.objects.filter(
                        renewal__create_user_id=user_id,
                        status=3
                    )
                    if renewal_log_objs:
                        response.code = 301
                        response.msg = '修改金额申请中, 请勿重复操作！'
                    else:
                        models.update_renewal_log.objects.create(
                            renewal_id=o_id,
                            price=obj.price,                    # 原 价格
                            original_price=obj.original_price,  # 原 原价
                            update_price=form_obj.cleaned_data.get('price'),                    # 现价格
                            update_original_price=form_obj.cleaned_data.get('original_price'),  # 现原价
                        )

                        response.code = 200
                        response.msg = '已申请, 请耐心等待!~'
                except Exception as e:
                    response.code = 301
                    response.msg = '操作异常'
            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())


    else:
        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)