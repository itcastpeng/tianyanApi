from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.renewal import AddForm, UpdateForm, SelectForm
from publicFunc import base64_encryption
import datetime, json

# cerf  token验证 用户展示模块
@account.is_token(models.Userprofile)
def renewal(request):
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
            }

            q = conditionCom(request, field_dict)

            print('q -->', q)
            objs = models.Userprofile.objects.filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            for obj in objs:
                brand_list = [i['name'] for i in obj.brand_classify.values('name')]
                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'name': base64_encryption.b64decode(obj.name),
                    'phone_number': obj.phone_number,
                    'signature': obj.signature,
                    'show_product': obj.show_product,
                    'register_date': obj.register_date.strftime('%Y-%m-%d'),
                    'overdue_date': obj.overdue_date.strftime('%Y-%m-%d'),
                    'set_avator': obj.set_avator,
                    'qr_code': obj.qr_code,
                    'brand_list': brand_list,
                    'vip_type': obj.get_vip_type_display(),
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
                'signature': "个性签名",
                'show_product': "文章底部是否显示产品",
                'register_date': "注册时间",
                'overdue_date': "过期时间",
                'set_avator': "头像",
                'qr_code': "微信二维码",
                'vip_type': "会员类型",
                'brand_list': "公司/品牌列表",
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
def renewal_oper(request, oper_type, o_id):
    response = Response.ResponseObj()

    form_data = {
        'o_id':o_id,
        'user_id':request.GET.get('user_id'),
        'price':request.POST.get('price'),
        'the_length':request.POST.get('the_length')
    }
    print('form_data------> ', form_data)
    if request.method == "POST":

        # 添加续费
        if oper_type == "add":
            form_obj = AddForm(form_data)
            if form_obj.is_valid():
                print('form_obj.data-------> ', form_obj.data)
                print(form_obj.data.get('the_length'))
                # models.renewal_management.objects.create(**{
                #     'price':form_obj.data.get('price'),
                #     'the_length':the_length,
                #     'renewal_number_days':renewal_number_days,
                #     'create_user_id':form_obj.data.get('user_id')
                # })
                # response.code = 200
                # response.msg = '添加成功'

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 修改续费
        elif oper_type == "update":
            form_obj = AddForm(form_data)
            if form_obj.is_valid():
                pass
            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 删除续费
        elif oper_type == "delete":
            form_obj = AddForm(form_data)
            if form_obj.is_valid():
                pass
            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = '请求异常'

    return JsonResponse(response.__dict__)
