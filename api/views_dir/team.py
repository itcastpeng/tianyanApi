from django.shortcuts import render, redirect
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.team import AddForm, UpdateForm, SelectForm, SelectUserListForm, DeleteMemberForm, SetManagementForm
from publicFunc import base64_encryption
from publicFunc.weixin import weixin_gongzhonghao_api
from api.views_dir.wechat import updateUserInfo
import requests, json
from publicFunc.host import host_url
from django.shortcuts import redirect
from publicFunc.forwarding_article import forwarding_article
from urllib.parse import unquote,quote
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
            objs = models.UserprofileTeam.objects.select_related('team').filter(
                user_id=user_id,
            ).order_by(order)
            # objs = models.Article.objects.select_related('classify').filter(q).order_by(order)
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []

            # 此处代码需要优化，设计多次数据库查询
            for obj in objs:
                #  将查询出来的数据 加入列表
                team_id = obj.team_id
                team_name = obj.team.name

                team_admin_user_id_list = [i[0] for i in
                                           models.UserprofileTeam.objects.filter(team_id=team_id, type=2).values_list(
                                               'user_id')]
                ret_data.append({
                    'id': team_id,
                    'name': team_name,
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'count': models.UserprofileTeam.objects.filter(team_id=team_id).count(),
                    'create_user_id': obj.team.create_user_id,
                    'team_admin_user_id_list': team_admin_user_id_list
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
            }

            response.note = {
                'id': "团队id",
                'name': "团队名称",
                'create_datetime': "创建时间",
                'count': "团队总人数",
                'create_user_id': "创建团队用户id",
                'team_admin_user_id_list': "团队管理员列表",
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
    # print('oper_type -->', oper_type)
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # 添加团队
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
                obj.userprofileteam_set.create(
                    user_id=user_id,
                    team_id=obj.id,
                    type=2
                )
                response.code = 200
                response.msg = "添加成功"
                response.data = {'id': obj.id}
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改团队名称
        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,  # 团队id
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

        # 删除团队成员
        elif oper_type == "delete_member":
            delete_user_id = request.POST.get('delete_user_id')  # 要移除的成员id
            form_data = {
                'o_id': o_id,  # 团队id
                'user_id': user_id,
                'delete_user_id': delete_user_id,
            }

            forms_obj = DeleteMemberForm(form_data)
            if forms_obj.is_valid():
                # print("验证通过")
                # print(forms_obj.cleaned_data)
                team_id = forms_obj.cleaned_data['o_id']
                delete_user_id_list = forms_obj.cleaned_data['delete_user_id']
                print('team_id -->', team_id)
                print('delete_user_id -->', delete_user_id)
                # 删除团队中的成员
                models.UserprofileTeam.objects.filter(
                    team_id=team_id,
                    type=1,
                    user_id__in=delete_user_id_list
                ).delete()

                response.code = 200
                response.msg = "删除成功"

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 设置普通成员成为管理员
        elif oper_type == "set_management":
            print('request.POST -->', request.POST)
            print('request.GET -->', request.GET)
            set_user_id = request.POST.get('set_user_id')
            print('set_user_id -->', set_user_id)
            form_data = {
                'o_id': o_id,  # 团队id
                'user_id': user_id,
                'set_user_id': set_user_id,
            }

            forms_obj = SetManagementForm(form_data)
            if forms_obj.is_valid():
                set_user_id_list = forms_obj.cleaned_data.get('set_user_id')
                team_id = forms_obj.cleaned_data.get('o_id')

                # 先将所有成员改成普通用户
                models.UserprofileTeam.objects.filter(team_id=team_id).update(type=1)

                # 修改成员类型为管理员
                models.UserprofileTeam.objects.filter(
                    team_id=team_id,
                    user_id__in=set_user_id_list
                ).update(type=2)

                response.code = 200
                response.msg = "修改成功"
            else:
                response.code = 301
                response.data = json.loads(forms_obj.errors.as_json())

    else:
        # 查看团队人员列表
        if oper_type == "select_user_list":
            form_data = {
                'team_id': o_id,
                'current_page': request.GET.get('current_page', 1),
                'length': request.GET.get('length', 10),
            }
            forms_obj = SelectUserListForm(form_data)
            if forms_obj.is_valid():
                print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
                current_page = forms_obj.cleaned_data['current_page']
                length = forms_obj.cleaned_data['length']
                team_id = forms_obj.cleaned_data['team_id']
                order = request.GET.get('order', 'create_datetime')
                field_dict = {
                    'id': '',
                    'type': '',
                    # 'user__name': '__contains',
                    'create_datetime': '',
                }
                q = conditionCom(request, field_dict)

                print('q -->', q)
                objs = models.UserprofileTeam.objects.select_related('user').filter(q).filter(
                    team_id=team_id
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
                    print('base64_encryption.b64encode(obj.user.name) -->', base64_encryption.b64encode(obj.user.name))
                    ret_data.append({
                        'id': obj.user_id,
                        'user_type_name': obj.get_type_display(),
                        'user_type': obj.type,
                        'name': base64_encryption.b64decode(obj.user.name),
                        'set_avator': obj.user.set_avator,
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
                    'user_type': "用户在团队中的类型/角色id,  1 ==> 普通用户   2 ==> 管理员",
                    'user_type_name': "用户在团队中的类型/角色名称",
                    'set_avator': "用户头像",
                    'create_datetime': "用户加入时间",
                }
            else:
                response.code = 301
                response.data = json.loads(forms_obj.errors.as_json())


    return JsonResponse(response.__dict__)


# 邀请成员 客户操作
def customer_invite_members(request, oper_type, o_id):
    response = Response.ResponseObj()
    print('rinvite_qrcodeequest.GET-----------> ', request.GET)
    print('rinvite_qrcodeequest.GET-----------> ', oper_type)
    print('reinvite_qrcodequest.POST-----------> ', o_id)


    # 客户点击确认邀请
    if oper_type == 'invite_members':
        code = request.GET.get('code')
        code_objs = models.save_code.objects.filter(save_code=code)
        if not code_objs:
            models.save_code.objects.create(save_code=code)

        team_id = o_id  # 团队id
        inviter_user_id = request.GET.get('state')  # 邀请人id
        weichat_api_obj = weixin_gongzhonghao_api.WeChatApi()
        ret_obj = weichat_api_obj.get_openid(code)
        openid = ret_obj.get('openid')
        user_id = updateUserInfo(openid, inviter_user_id, ret_obj)

        # 添加该成员到团队中
        objs = models.UserprofileTeam.objects.filter(team_id=team_id, user_id=user_id)
        if not objs:
            models.UserprofileTeam.objects.create(team_id=team_id, user_id=user_id)

        obj = models.Userprofile.objects.get(id=user_id)
        # 此处跳转到天眼首页
        url = 'http://zhugeleida.zhugeyingxiao.com/tianyan/?token={token}&user_id={user_id}'.format(
            token=obj.token,
            user_id=user_id
        )
        response.code = 200
        response.msg = "邀请成功"
        return redirect(url)


    # 邀请成员页面跳转 显示确认邀请页面
    elif oper_type == 'invitation_page':
        user_id = request.GET.get('state')
        obj = models.UserprofileTeam.objects.select_related('team', 'user').get(team_id=o_id, user_id=user_id)

        team_name = obj.team.name  # 团队名称
        user_name = base64_encryption.b64decode(obj.user.name)  # 客户名称
        set_avator = obj.user.set_avator  # 客户头像

        url = '{host_url}api/invite_members/invite_members/{o_id}'.format(
            host_url=host_url,
            o_id=o_id,  # 团队ID
        )

        redirect_uri = forwarding_article(pub=1, user_id=user_id, redirect_uri=url)
        print('redirect_uri------------======------------> ', unquote(redirect_uri))
        redirect_url = '{host_url}#/share_invited_member?team_name={team_name}&user_name={user_name}&set_avator={set_avator}&redirect_uri={redirect_uri}'.format(
            host_url=host_url,
            team_name=team_name,
            user_name=user_name,
            set_avator=set_avator,
            redirect_uri=redirect_uri,
        )
        return redirect(redirect_url)

    return JsonResponse(response.__dict__)