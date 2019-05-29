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
            'role_id': '',
            'create_date': '',
            'oper_user__username': '__contains',
        }

        q = conditionCom(request, field_dict)

        objs = models.userprofile.objects.select_related('role').filter(q).order_by(order)

        count = objs.count()

        if length != 0:
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            objs = objs[start_line: stop_line]

        # 返回的数据
        ret_data = []
        now = datetime.date.today()
        for obj in objs:
            last_login_time = ''
            if obj.last_login_time:
                last_login_time = obj.last_login_time.strftime('%Y-%m-%d %H:%M:%S')
            #  将查询出来的数据 加入列表
            ret_data.append({
                'id': obj.id,
                'username': obj.username,                           # 用户名称
                'role_id': obj.role_id,                             # 角色ID
                'role__name': obj.role.name,                        # 角色名称
                'oper_user__username':obj.oper_user.username,       # 操作人
                'oper_user_id': obj.oper_user_id,                   # 操作人ID
                'status': obj.status,                               # 用户状态ID
                'get_status_display': obj.get_status_display(),     # 用户状态 (审核, 未审核)
                'set_avator': obj.set_avator,                       # 头像
                'phone': obj.phone,                                 # 电话
                'last_login_time': last_login_time,                 # 最后一次登录时间
                'create_time': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            })

        #  查询成功 返回200 状态码
        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'ret_data': ret_data,
            'data_count': count,
            'status':models.userprofile.status_choices
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
# @account.is_token(models.Enterprise)
def user_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":
        # 获取需要修改的信息
        form_data = {
            'o_id': o_id,
            'name': request.POST.get('name'),                   # 用户名
            'password': request.POST.get('password'),           # 密码

            'role': request.POST.get('role', 1),                # 角色 默认用户
            'oper_user_id': request.GET.get('oper_user_id'),    # 操作人
            'phone': request.POST.get('phone'),                 # 电话
            'appid': request.POST.get('appid'),                 # appid
            'appsecret': request.POST.get('appsecret'),         # appsecret
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
                username = forms_obj.cleaned_data['username']           # 用户名
                role_id = forms_obj.cleaned_data['role_id']             # 角色ID
                oper_user_id = forms_obj.cleaned_data['oper_user_id']   # 操作人
                set_avator = forms_obj.cleaned_data['set_avator']       # 头像
                phone = forms_obj.cleaned_data['phone']                 # 电话

                objs = models.userprofile.objects.filter(
                    id=o_id
                )
                #  更新 数据
                if objs:
                    objs.update(
                        username=username,
                        role_id=role_id,
                        oper_user_id=oper_user_id,
                        phone=phone,
                        set_avator=set_avator
                    )

                    response.code = 200
                    response.msg = "修改成功"

                else:
                    response.code = 303
                    response.msg = '修改ID不存在'

            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除 用户
        elif oper_type == "delete":
            if o_id == user_id:
                response.code = 301
                response.msg = '不能删除自己'
            else:
                objs = models.userprofile.objects.get(id=o_id)
                if objs:
                    objs.delete()
                    response.code = 200
                    response.msg = "删除成功"
                else:
                    response.code = 302
                    response.msg = '删除ID不存在'
            response.data = {}

    else:
        # 用户审核
        if oper_type == 'user_audit':
            objs = models.userprofile.objects.filter(id=o_id)
            if objs:
                if int(objs[0].status) == 1:
                    objs[0].status = 2
                else:
                    objs[0].status = 1
                objs[0].save()
                response.code = 200
                response.msg = '修改成功'

            else:
                response.code = 301
                response.msg = '无此用户'

        # 获取用户信息
        elif oper_type == 'get_user_info':
            obj = models.userprofile.objects.get(id=user_id)

            response.code = 200
            response.msg = '查询个人信息成功'
            response.data = {
                'set_avator': obj.set_avator,
                'username': obj.username,
                'role_id': obj.role_id,
            }

        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)

