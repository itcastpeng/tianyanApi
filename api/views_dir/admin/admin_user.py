from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from api.forms.admin.admin_user import AddForm, UpdateForm, SelectForm
import json, datetime, time


# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.Enterprise)
def user(request):
    response = Response.ResponseObj()
    forms_obj = SelectForm(request.GET)
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        order = request.GET.get('order', '-create_date')

        field_dict = {
            'id': '',
            'status': '',
            'role': '',
            'create_date': '',
            'oper_user__name': '__contains',
        }

        q = conditionCom(request, field_dict)

        objs = models.Enterprise.objects.filter(
            q,
        ).order_by(order)

        count = objs.count()

        if length != 0:
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            objs = objs[start_line: stop_line]

        # 返回的数据
        ret_data = []
        for obj in objs:
            ret_data.append({
                'id': obj.id,                                               # 用户ID
                'name': obj.name,                                           # 用户名称
                'role': obj.role,                                           # 角色ID
                'role_name': obj.get_role_display(),                        # 角色名称
                'status':obj.status,                                        # 状态ID
                'status_name':obj.get_status_display(),                     # 状态
                'appid': obj.appid,                                         # appid
                'appsecret': obj.appsecret,                                 # appsecret
                'phone': obj.phone,                                         # 电话
                'create_time': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            })

        #  查询成功 返回200 状态码
        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'ret_data': ret_data,
            'data_count': count,
            'status':models.Enterprise.status_choices
            }

    else:
        response.code = 301
        response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)


# 修改密码
@csrf_exempt
@account.is_token(models.Enterprise)
def updatePwd(request):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    user_objs = models.userprofile.objects.filter(id=user_id)

    if user_objs:
        user_obj = user_objs[0]
        oldPwd = request.POST.get('oldPwd')
        newPwd = request.POST.get('newPwd')

        if newPwd and oldPwd:
            oldPwd = account.str_encrypt(oldPwd) # 加密 密码
            if oldPwd == user_obj.password:
                newPwd = account.str_encrypt(newPwd)
                token = account.get_token(newPwd + str(int(time.time()) * 1000)) #  token
                user_objs.update(password=newPwd, token=token)
                response.code = 200
                response.msg = '修改成功'
            else:
                response.code = 301
                response.msg = '旧密码验证错误'
        else:
            if not oldPwd:
                response.msg = '请输入旧密码'
            else:
                response.msg = '请输入新密码'
            response.code = 301
    else:
        response.code = 500
        response.msg = '非法请求'

    return JsonResponse(response.__dict__)


@csrf_exempt
@account.is_token(models.Enterprise)
def user_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":
        # 获取需要修改的信息

        role = int(request.POST.get('role', 1))
        appid = request.POST.get('appid')
        appsecret = request.POST.get('appsecret')
        if role == 2: # 超級管理员
            appid = ''
            appsecret = ''

        form_data = {
            'o_id': o_id,
            'oper_user_id': request.GET.get('user_id', 1),      # 操作人
            'name': request.POST.get('name'),                   # 用户名
            'password': request.POST.get('password'),           # 密码
            'role': role,                                       # 角色 默认用户
            'phone': request.POST.get('phone'),                 # 电话
            'appid': appid,                                     # appid
            'appsecret': appsecret,                             # appsecret
        }

        # 添加用户
        if oper_type == "add":
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                models.Enterprise.objects.create(**forms_obj.cleaned_data)

                response.code = 200
                response.msg = "添加成功"

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改用户
        elif oper_type == "update":
            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                o_id = forms_obj.cleaned_data['o_id']
                name = forms_obj.cleaned_data['name']       # 用户名
                phone = forms_obj.cleaned_data['phone']     # 电话

                objs = models.Enterprise.objects.filter(
                    id=o_id
                )
                #  更新 数据
                if objs:
                    objs.update(
                        name=name,
                        phone=phone,
                    )
                    response.code = 200
                    response.msg = "修改成功"

                else:
                    response.code = 303
                    response.msg = '修改ID不存在'

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:

        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)

