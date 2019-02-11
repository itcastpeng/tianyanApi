from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse

from publicFunc.condition_com import conditionCom
from api.forms.article import AddForm, UpdateForm, SelectForm, UpdateClassifyForm
import json

from django.db.models import Q


# token验证 用户展示模块
# @account.is_token(models.Userprofile)
def article(request):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'title': '__contains',
                'classify_id': '__in',
                'create_user_id': '__in',
                'create_datetime': '',
                'source_link': '',
            }
            q = conditionCom(request, field_dict)
            classify_type = forms_obj.cleaned_data.get('classify_type')    # 分类类型，1 => 推荐, 2 => 品牌
            user_obj = models.Userprofile.objects.get(id=user_id)

            classify_objs = None
            if classify_type == 1:  # 推荐分类
                classify_objs = user_obj.recommend_classify.all()
            elif classify_type == 2:    # 品牌分类
                classify_objs = user_obj.brand_classify.all()

            if classify_objs:
                classify_id_list = [obj.id for obj in classify_objs]
                print("classify_id_list -->", classify_id_list)
                if len(classify_id_list) > 0:
                    q.add(Q(**{'classify_id__in': classify_id_list}), Q.AND)

            print('q -->', q)
            objs = models.Article.objects.select_related('classify').filter(q).order_by(order)
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
                    'title': obj.title,
                    'content': obj.content,
                    'look_num': obj.look_num,
                    'like_num': obj.like_num,
                    'classify_id': obj.classify_id,
                    'classify_name': obj.classify.name,
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                })
            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'data_count': count,
                'is_customer':forms_obj.cleaned_data['id'] # 判断是否为客户查看 (该字段有值 为客户查看详情 调用接口返回时长)
            }

            response.note = {
                'id': "文章id",
                'title': "文章标题",
                'content': "文章内容",
                'look_num': "查看次数",
                'like_num': "点赞(喜欢)次数",
                'classify_id': "所属分类id",
                'classify_name': "所属分类名称",
                'create_datetime': "创建时间",
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
def article_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":
        if oper_type == "add":
            form_data = {
                'create_user_id': user_id,
                'title': request.POST.get('title'),
                'content': request.POST.get('content'),
                'classify_id': request.POST.get('classify_id'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                # print(forms_obj.cleaned_data)
                #  添加数据库
                # print('forms_obj.cleaned_data-->',forms_obj.cleaned_data)
                obj = models.Article.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
                response.data = {'id': obj.id}
            else:
                print("验证不通过")
                # print(forms_obj.errors)
                response.code = 301
                # print(forms_obj.errors.as_json())
                response.msg = json.loads(forms_obj.errors.as_json())

        # elif oper_type == "delete":
        #     # 删除 ID
        #     objs = models.company.objects.filter(id=o_id)
        #     if objs:
        #         objs.delete()
        #         response.code = 200
        #         response.msg = "删除成功"
        #     else:
        #         response.code = 302
        #         response.msg = '删除ID不存在'
        
        # 修改文章
        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,   # 文章id
                'create_user_id': user_id,
                'title': request.POST.get('title'),
                'content': request.POST.get('content'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                title = forms_obj.cleaned_data['title']
                content = forms_obj.cleaned_data['content']

                #  查询更新 数据
                models.Article.objects.filter(id=o_id).update(
                    title=title,
                    content=content,
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

        # 修改文章所属分类
        elif oper_type == "update_classify":
            form_data = {
                'o_id': o_id,  # 文章id
                'create_user_id': user_id,
                'classify_id': request.POST.get('classify_id'),
            }

            forms_obj = UpdateClassifyForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                classify_id = forms_obj.cleaned_data['classify_id']

                #  查询更新 数据
                models.Article.objects.filter(id=o_id).update(
                    classify_id=classify_id,
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
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
