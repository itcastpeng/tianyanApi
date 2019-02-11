from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.posters import AddForm, UpdateForm, SelectForm
import json


# token验证 海报展示模块
@account.is_token(models.Userprofile)
def posters(request):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']

            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'posters_url': '__contains',
                'posters_status': '',
                'create_datetime': '',
                'create_user_id': '',
                'create_user__name': '__contains',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            objs = models.Posters.objects.filter(q).order_by(order)
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
                    'posters_url': obj.posters_url,
                    'posters_status_id': obj.posters_status,
                    'posters_status': obj.get_posters_status_display(),
                    'create_user_id': obj.create_user_id,
                    'create_user__name': obj.create_user.name,
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                })

            posters_choices = []
            for i in models.Posters.posters_choices:
                posters_choices.append({
                    'id':i[0],
                    'name':i[1]
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
                'posters_choices': posters_choices,
            }

            response.note = {
                'id': "海报ID",
                'posters_url': "海报链接",
                'posters_status_id': "海报类型ID",
                'posters_status': "海报类型名称",
                'create_datetime': "创建时间",
                'create_user_id': "创建人ID",
                'create_user__name': "创建人名字",
            }

        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


# 海报增删改
# token验证
@account.is_token(models.Userprofile)
def posters_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')

    if request.method == "POST":
        form_data = {
            'o_id':o_id,
            'create_user_id': user_id,
            'posters_url': request.POST.get('posters_url'),
            'posters_status': request.POST.get('posters_status', 1),
        }

        # 添加海报
        if oper_type == "add":
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                obj = models.Posters.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
                response.data = {'id': obj.id}
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())
        
        # 修改海报
        elif oper_type == "update":
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                o_id, objs = forms_obj.cleaned_data['o_id']
                posters_url = forms_obj.cleaned_data['posters_url']
                posters_status = forms_obj.cleaned_data['posters_status']

                objs.update(posters_url=posters_url, posters_status=posters_status)
                response.code = 200
                response.msg = "修改成功"

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除海报
        elif oper_type == "delete":
            # 删除 ID
            objs = models.Posters.objects.filter(id=o_id)
            if objs:
                objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '删除ID不存在'

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)