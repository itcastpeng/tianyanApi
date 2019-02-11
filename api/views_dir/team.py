from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse

from publicFunc.condition_com import conditionCom
from api.forms.team import AddForm, UpdateForm, SelectForm
import json

from django.db.models import Q
from publicFunc import base64_encryption


# token验证 用户展示模块
@account.is_token(models.Userprofile)
def team(request):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', 'create_datetime')
            # field_dict = {
            #     'id': '',
            #     'name': '__contains',
            #     'create_datetime': '',
            # }
            # q = conditionCom(request, field_dict)
            # classify_type = forms_obj.cleaned_data.get('classify_type')    # 分类类型，1 => 推荐, 2 => 品牌
            user_obj = models.Userprofile.objects.get(id=user_id)
            objs = user_obj.team.all().order_by(order)
            # objs = models.Article.objects.select_related('classify').filter(q).order_by(order)
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
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'count': obj.userprofile_team.count()
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }

            response.note = {
                'id': "文章id",
                'name': "团队名称",
                'create_datetime': "创建时间",
                'count': "团队总人数",
            }
        else:
            response.code = 301
            response.data = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)


# 增删改
# token验证
@account.is_token(models.Userprofile)
def team_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # 添加
        if oper_type == "add":
            form_data = {
                'create_user_id': user_id,
                'name': request.POST.get('name'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                # print(forms_obj.cleaned_data)
                #  添加数据库
                # print('forms_obj.cleaned_data-->',forms_obj.cleaned_data)
                obj = models.Team.objects.create(**forms_obj.cleaned_data)
                obj.userprofile_team.add(user_id)
                response.code = 200
                response.msg = "添加成功"
                response.data = {'id': obj.id}
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改
        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,   # 团队id
                'user_id': user_id,
                'name': request.POST.get('name'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                # print("验证通过")
                # print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                name = forms_obj.cleaned_data['name']

                #  查询更新 数据
                models.Team.objects.filter(id=o_id).update(
                    name=name,
                )

                response.code = 200
                response.msg = "修改成功"

            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                #  字符串转换 json 字符串
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        # 查看团队人员列表
        if oper_type == "select_user_list":
            form_data = {
                'team_id': o_id,
                'current_page': request.GET.get('current_page', 1),
                'length': request.GET.get('length', 10),
            }
            forms_obj = SelectForm(form_data)
            if forms_obj.is_valid():
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                team_id = forms_obj.cleaned_data['team_id']
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
                order = request.GET.get('order', 'create_datetime')
                # field_dict = {
                #     'id': '',
                #     'name': '__contains',
                #     'create_datetime': '',
                # }
                # q = conditionCom(request, field_dict)
                # classify_type = forms_obj.cleaned_data.get('classify_type')    # 分类类型，1 => 推荐, 2 => 品牌

                team_obj = models.Team.objects.get(id=team_id)
                objs = team_obj.userprofile_team.all().order_by(order)
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
                        'name': base64_encryption.b64decode(obj.name),
                        'set_avator': obj.set_avator,
                        'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
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
                    'name': "用户名称",
                    'set_avator': "用户头像",
                    'create_datetime': "用户加入时间"
                }
            else:
                response.code = 301
                response.data = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)
