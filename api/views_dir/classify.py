from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.classify import AddForm, UpdateForm, SelectForm
import json


# token验证 用户展示模块
@account.is_token(models.Userprofile)
def classify(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            # current_page = forms_obj.cleaned_data['current_page']
            # length = forms_obj.cleaned_data['length']
            print('forms_obj.cleaned_data -->', forms_obj.cleaned_data)
            user_id = request.GET.get('user_id')
            recommended_classifiy = request.GET.get('recommended_classifiy') # 是否选择默认分类 create_user 为空
            order = request.GET.get('order', '-create_datetime')
            field_dict = {
                'id': '',
                'name': '__contains',
                'create_datetime': '',
            }
            q = conditionCom(request, field_dict)
            print('q -->', q)
            if recommended_classifiy: # 默认分类
                objs = models.Classify.objects.filter(q, create_user__isnull=True).order_by(order)
            else: # 品牌分类
                objs = models.Classify.objects.filter(q, create_user__isnull=False).order_by(order)

            count = objs.count()

            # if length != 0:
            #     start_line = (current_page - 1) * length
            #     stop_line = start_line + length
            #     objs = objs[start_line: stop_line]

            # 返回的数据
            ret_data = []
            user_obj = models.Userprofile.objects.get(id=user_id)
            recommend_classify_obj = [i.id for i in user_obj.recommend_classify.all()]
            print('recommend_classify_obj------> ', recommend_classify_obj)
            for obj in objs:
                # 查询推荐分类是否打钩
                is_check_whether = False
                if obj.id in recommend_classify_obj:
                    is_check_whether = True

                #  将查询出来的数据 加入列表
                ret_data.append({
                    'id': obj.id,
                    'name': obj.name,
                    'is_check_whether': is_check_whether,
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
                'id': "分类id",
                'name': '分类名称',
                'create_datetime': '创建时间',
            }
        else:
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


# 增删改
# token验证
@account.is_token(models.Userprofile)
def classify_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    if request.method == "POST":
        if oper_type == "add":
            form_data = {
                'user_id': o_id,
                'oper_user_id': request.GET.get('user_id'),
                'name': request.POST.get('name'),
            }
            #  创建 form验证 实例（参数默认转成字典）
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                obj = models.Classify.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
                response.data = {'testCase': obj.id}
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # elif oper_type == "delete":
        #     # 删除 ID
        #     objs = models.Classify.objects.filter(id=o_id)
        #     if objs:
        #         objs.delete()
        #         response.code = 200
        #         response.msg = "删除成功"
        #     else:
        #         response.code = 302
        #         response.msg = '删除ID不存在'
        elif oper_type == "update":
            # 获取需要修改的信息
            form_data = {
                'o_id': o_id,
                'name': request.POST.get('name'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                print(forms_obj.cleaned_data)
                o_id = forms_obj.cleaned_data['o_id']
                name = forms_obj.cleaned_data['name']
                #  查询数据库  用户id
                objs = models.Classify.objects.filter(
                    id=o_id
                )
                #  更新 数据
                if objs:
                    objs.update(
                        name=name
                    )

                    response.code = 200
                    response.msg = "修改成功"
                else:
                    response.code = 303
                    response.msg = json.loads(forms_obj.errors.as_json())
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

    else:
        response.code = 402
        response.msg = "请求异常"

    return JsonResponse(response.__dict__)
