# from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from django.db.models import Q
from publicFunc.condition_com import conditionCom
from api.forms.small_shop import AddForm, UpdateForm, SelectForm
import json


# 分组树状图（包含测试用例详情）
def testGroupTree(oper_user_id, parent_classify_id=None):
    result_data = []
    q = Q()
    q.add(Q(oper_user_id=oper_user_id) & Q(parent_classify_id=parent_classify_id), Q.AND)
    objs = models.GoodsClassify.objects.filter(q)
    for obj in objs:
        parent_id = ''
        parent_classify_goods_classify = ''
        if obj.parent_classify_id:
            parent_id = obj.parent_classify_id
            parent_classify_goods_classify = obj.parent_classify.goods_classify

        current_data = {
            'id': obj.id,
            'goods_classify': obj.goods_classify,
            'parent_classify_id': parent_id,
            'parent_classify_goods_classify': parent_classify_goods_classify,
            'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'expand': False,
            'checked': False,
        }
        if parent_classify_id:
            children_data = testGroupTree(oper_user_id, obj.id)
            current_data['children'] = children_data
        result_data.append(current_data)
    return result_data


# token验证 微店展示模块
@account.is_token(models.Userprofile)
def goods_classify(request):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    parent_classify_id = request.GET.get('parent_classify_id')
    if request.method == "GET":

        data_list = testGroupTree(user_id, parent_classify_id=parent_classify_id)
        response.code = 200
        response.msg = '查询成功'
        response.data = {
            'ret_data': data_list,
        }
        response.note = {
            'id': '商品分类ID',
            'goods_classify': '商品分类名称',
            'create_datetime': '该商品分类创建时间',
            'parent_classify_goods_classify': '分类父级名称',
            'parent_classify_id': '分类父级ID',
        }
    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)


# 微店增删改
# token验证
@account.is_token(models.Userprofile)
def goods_classify_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # 添加商品分类
        if oper_type == "add_classify":
            form_data = {
                'oper_user_id': user_id,
                'goods_classify': request.POST.get('goods_classify'),
                'parent_classify_id': request.POST.get('parent_classify_id'),
            }
            forms_obj = AddForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                obj = models.GoodsClassify.objects.create(**forms_obj.cleaned_data)
                response.code = 200
                response.msg = "添加成功"
                response.data = {'id': obj.id}
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改商品分类
        elif oper_type == "update_classify":
            form_data = {
                'o_id': o_id,
                'oper_user_id': user_id,
                'goods_classify': request.POST.get('goods_classify'),
                'parent_classify_id': request.POST.get('parent_classify_id'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                o_id, objs = forms_obj.cleaned_data['o_id']
                goods_classify = forms_obj.cleaned_data['goods_classify']
                parent_classify_id = forms_obj.cleaned_data['parent_classify_id']

                #  查询更新 数据
                objs.update(
                    goods_classify=goods_classify,
                    parent_classify_id=parent_classify_id,
                )

                response.code = 200
                response.msg = "修改成功"

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除商品分类
        elif oper_type == "delete_classify":
            # 删除 ID
            objs = models.GoodsClassify.objects.filter(id=o_id)
            if objs:
                if models.Goods.objects.filter(goods_classify_id=o_id):
                    response.code = 301
                    response.msg = '请先移除该分类下商品'
                else:
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
