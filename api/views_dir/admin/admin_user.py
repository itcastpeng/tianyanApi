from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from publicFunc.condition_com import conditionCom
from api.forms.admin.admin_user import AddForm, UpdateForm, SelectForm
from django.db.models import Q
from publicFunc.public import length_the_days
import json, datetime, time


# cerf  token验证 用户展示模块
@csrf_exempt
@account.is_token(models.Enterprise)
def user(request):
    print('request.GET--------> ', request.GET)
    response = Response.ResponseObj()
    forms_obj = SelectForm(request.GET)
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        order = request.GET.get('order', '-create_date')
        user_id, role = forms_obj.cleaned_data.get('user_id')
        field_dict = {
            'id': '',
            'status': '',
            'role': '',
            'create_date': '',
            'oper_user__name': '__contains',
            'oper_user_id': '',
        }

        q = conditionCom(request, field_dict)
        q1 = Q()
        if int(role) == 1: # 普通用户
            q1.add(Q(oper_user_id=user_id), Q.AND)

        objs = models.Enterprise.objects.filter(
            q,
            q1
        ).order_by(order).exclude(id=user_id)

        count = objs.count()

        if length != 0:
            start_line = (current_page - 1) * length
            stop_line = start_line + length
            objs = objs[start_line: stop_line]

        now = datetime.datetime.today()
        # 返回的数据
        ret_data = []
        for obj in objs:
            obj.working_days = (now - obj.create_date).days
            obj.save()

            ret_data.append({
                'id': obj.id,                                               # 用户ID
                'name': obj.name,                                           # 用户名称
                'role': obj.role,                                           # 角色ID
                'role_name': obj.get_role_display(),                        # 角色名称
                'status':obj.status,                                        # 审核ID
                'status_name':obj.get_status_display(),                     # 是否审核
                'appid': obj.appid,                                         # appid
                'phone': obj.phone,                                         # 电话
                'create_time': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                'primary_distribution': obj.primary_distribution,           # 一级占比
                'secondary_distribution': obj.secondary_distribution,       # 二级占比
                'working_days': (now - obj.create_date).days,                           # 合作天数
            })

        #  查询成功 返回200 状态码
        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'ret_data': ret_data,
            'data_count': count,
            'status':models.Enterprise.status_choices
            }
        response.note = {
            'name': '用户名称',
            'role': '角色ID',
            'role_name': '角色名称',
            'status': '审核ID',
            'status_name': '是否审核',
            'appid': 'appid',
            'phone': '电话',
            'create_time': '创建时间',
            'primary_distribution': '一级占比',
            'secondary_distribution': '二级占比',
            'working_days': '合作天数'
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
    user_objs = models.Enterprise.objects.filter(id=user_id)

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
    role = int(models.Enterprise.objects.get(id=user_id).role)
    if request.method == "POST":
        # 获取需要修改的信息
        flag = True
        form_data = {
            'o_id': o_id,
            'oper_user_id': request.GET.get('user_id'),         # 操作人
            'name': request.POST.get('name'),                   # 用户名
            'password': request.POST.get('password'),           # 密码
            'role': 1,                                          # 角色
            'phone': request.POST.get('phone'),                 # 电话
        }

        # 添加用户
        if oper_type == "add":
            flag = False
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
            flag = False
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

        # 修改 分销占比
        elif oper_type  == 'distribution':
            flag = False
            primary_distribution = request.POST.get('primary_distribution') # 一级占比
            secondary_distribution = request.POST.get('secondary_distribution') # 二级占比
            if primary_distribution and secondary_distribution:

                # 记录日志
                now = datetime.datetime.today()
                objs = models.distribution_log.objects.filter(
                    create_user_id=user_id
                ).order_by(
                    '-create_date'
                )

                if objs.filter(status=3).count() >= 1:
                    response.code = 301
                    response.msg = '请勿重复操作, 审核中！'
                else:
                    if objs:
                        obj = objs[0]
                        obj.stop_time = now.strftime('%Y-%m-%d %H:%M:%S')
                        obj.save()

                    user_obj = models.Enterprise.objects.get(id=user_id)

                    models.distribution_log.objects.create(
                        create_user_id=user_id,
                        old_primary_distribution=user_obj.primary_distribution, # 旧数据
                        old_secondary_distribution=user_obj.secondary_distribution, #  旧数据
                        primary_distribution=primary_distribution,
                        secondary_distribution=secondary_distribution,
                        stop_time='至今'
                    )
                    response.code = 200
                    response.msg = '等待审核, 请耐心等待'

            else:
                response.code = 301
                if primary_distribution:
                    msg = '二级分销不能为空'
                else:
                    msg = '一级分销不能为空'
                response.msg = msg

        if flag:
            if role == 2: # (管理员 role=2)

                # 审核用户
                if oper_type == 'review_user':
                    status = int(request.POST.get('status'))
                    if status in [1, 3]:
                        objs = models.Enterprise.objects.filter(
                            id=o_id,
                            status__in=[2, 3]
                        )
                        obj = objs[0]
                        objs.update(status=status)
                        msg = '审核驳回'
                        if status == 1:
                            msg = '审核通过'

                            # 创建默认会员价格
                            data = [
                                {
                                    'the_length':1,
                                    'price':99,
                                    'original_price':199,
                                },
                                {
                                    'the_length': 2,
                                    'price': 299,
                                    'original_price': 499,
                                },
                                {
                                    'the_length': 3,
                                    'price': 599,
                                    'original_price': 999,
                                },
                            ]
                            for i in data:
                                the_length, renewal_number_days = length_the_days(i.get('the_length'))
                                models.renewal_management.objects.create(
                                    create_user_id=obj.id,
                                    price=i.get('price'),
                                    original_price=i.get('original_price'),
                                    renewal_number_days=renewal_number_days,
                                    the_length=the_length,
                                )


                        response.code = 200
                        response.msg = msg

                    else:
                        response.code = 301
                        response.msg = '审核异常'

                # 审核 修改续费
                elif oper_type == 'revise_renewal_review':
                    status = request.POST.get('status')
                    if status:
                        status = int(status)
                        obj = models.update_renewal_log.objects.get(id=o_id)
                        response.code = 200

                        response.msg = '审核驳回'
                        if status == 1:
                            renewal_objs = models.renewal_management.objects.filter(id=obj.renewal_id)
                            if renewal_objs:
                                renewal_obj = renewal_objs[0]
                                renewal_obj.price = obj.update_price
                                renewal_obj.original_price = obj.update_original_price
                                renewal_obj.save()
                                response.msg = '审核通过'

                        obj.status = status
                        obj.save()

                    else:
                        response.code = 301
                        response.msg = '审核异常'

                # 审核 修改分销占比
                elif oper_type == 'review_distribution':
                    status = int(request.POST.get('status'))
                    obj = models.distribution_log.objects.get(id=o_id)

                    objs = models.distribution_log.objects.filter(
                        create_user_id=obj.create_user_id,
                        status=1
                    ).order_by(
                        '-create_date'
                    )

                    if objs:
                        objs[1].stop_time = obj.create_date
                        objs[1].save()

                    obj.status = status
                    obj.save()
                    models.Enterprise.objects.filter(
                        id=obj.create_user_id
                    ).update(
                        primary_distribution=obj.primary_distribution,
                        secondary_distribution=obj.secondary_distribution,
                    )
                    response.code = 200
                    if status == 1:
                        response.msg = '审核成功'
                    else:
                        response.msg = '驳回成功'

            else:
                response.code = 301
                response.msg = '权限不足'

    else:
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            user_id, role = forms_obj.cleaned_data.get('user_id')
            admin = request.GET.get('admin') # 管理员查询

            # 修改分销 记录
            if oper_type == 'get_distribution':
                q = Q()
                order = request.GET.get('order', '-create_date')

                if admin:
                    q.add(Q(status=3), Q.AND)
                else:
                    q.add(Q(create_user_id=user_id), Q.AND)


                objs = models.distribution_log.objects.filter(
                    q,
                ).order_by(order)

                count = objs.count()
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    ret_data.append({
                        'id': obj.id,
                        'create_date': obj.create_date.strftime('%Y-%m-%d'),
                        'stop_time': obj.stop_time,
                        'primary_distribution': obj.primary_distribution, # 一级分销占比
                        'secondary_distribution': obj.secondary_distribution, # 二级分销占比
                        'old_primary_distribution': obj.old_primary_distribution, # 原一级分销占比
                        'old_secondary_distribution': obj.old_secondary_distribution, # 原二级分销占比
                        'status': obj.get_status_display(), # 审核状态
                        'create_user__name': obj.create_user.name, # 审核状态
                    })
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count
                }
                response.note = {
                    'create_date': '开始使用时间',
                    'stop_time': '结束时间',
                    'primary_distribution': '一级分销占比',
                    'secondary_distribution': '二级分销占比',
                }

            # 查询待审核用户
            elif oper_type == 'get_review_user':
                if role == 2:
                    objs = models.Enterprise.objects.filter(status=2)
                    count = objs.count()
                    if length != 0:
                        start_line = (current_page - 1) * length
                        stop_line = start_line + length
                        objs = objs[start_line: stop_line]

                    ret_data = []
                    for obj in objs:
                        ret_data.append({
                            'id': obj.id,
                            'name': obj.name,
                            'phone': obj.phone,
                            'appid': obj.appid,
                            'oper_user_id':obj.oper_user_id,
                            'oper_user___name':obj.oper_user.name,
                            'create_date':obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                        })

                    response.code = 200
                    response.msg = '查询成功'
                    response.data = {
                        'ret_data': ret_data,
                        'count': count
                    }
                else:
                    response.code = 301
                    response.msg = '权限不足'

            # 查询待审核 修改续费
            elif oper_type == 'get_revise_renewal_review':
                q = Q()
                if admin:
                    q.add(Q(status=3), Q.AND)
                else:
                    q.add(Q(renewal__create_user_id=user_id), Q.AND)

                objs = models.update_renewal_log.objects.filter(
                    q,
                ).order_by('-create_date')

                count = objs.count()
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]

                ret_data = []
                for obj in objs:
                    the_length = obj.renewal.get_the_length_display()

                    ret_data.append({
                        'id': obj.id,
                        'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'update_before_price': obj.price,
                        'update_before_original_price': obj.original_price,
                        'update_after_price': obj.update_price,
                        'update_after_original_price': obj.update_original_price,
                        'status': obj.get_status_display(),
                        'oper_user_name': obj.renewal.create_user.name,
                        'the_length': the_length,
                    })
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count
                }
                response.note = {
                    'update_before_price': '修改前价格',
                    'update_before_original_price': '修改前 原价',
                    'update_after_price': '修改后价格',
                    'update_after_original_price': '修改后 原价',
                    'status': '审核状态',
                    'oper_user_name': '操作人',
                    'the_length': '续费时长',
                }

            # 获取自己信息
            elif oper_type == 'get_user_info':
                obj = models.Enterprise.objects.get(id=user_id)
                ret_data = {
                    'id': obj.id,  # 用户ID
                    'name': obj.name,  # 用户名称
                    'role': obj.role,  # 角色ID
                    'role_name': obj.get_role_display(),  # 角色名称
                    'status': obj.status,  # 审核ID
                    'status_name': obj.get_status_display(),  # 是否审核
                    'phone': obj.phone,  # 电话
                    'create_time': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'primary_distribution': obj.primary_distribution,  # 一级占比
                    'secondary_distribution': obj.secondary_distribution,  # 二级占比
                }
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data
                }

            else:
                response.code = 402
                response.msg = "请求异常"

        else:
            response.code = 301
            response.msg = json.loads(forms_obj.errors.as_json())


    return JsonResponse(response.__dict__)




