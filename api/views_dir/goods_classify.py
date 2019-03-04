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
def testGroupTree(parent_category, parent_class_id=None):
    result_data = []
    q = Q()
    q.add(Q(parent_category=parent_category) & Q(parent_class_id=parent_class_id), Q.AND)
    objs = models.GoodsClassify.objects.filter(q)
    for obj in objs:
        current_data = {
            'id': obj.id,
            'classification_name':obj.classification_name,
            'expand': False,
            'checked': False,
        }
        children_data = testGroupTree(parent_category, obj.id)
        current_data['children'] = children_data
        result_data.append(current_data)

    return result_data

# token验证 微店展示模块
@account.is_token(models.Userprofile)
def goods_classify(request):
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
                'goods_classify': '',
                'oper_user_id': '__contains',
                'create_datetime': '',
            }
            q = conditionCom(request, field_dict)
            objs = models.GoodsClassify.objects.filter(q, oper_user_id=user_id).order_by(order)

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            data_list = []
            for obj in objs:

                parent_classify_id = ''
                parent_classify_goods_classify = ''
                if obj.parent_classify_id:
                    parent_classify_id = obj.parent_classify_id
                    parent_classify_goods_classify = obj.parent_classify.goods_classify

                data_list.append({
                    'id': obj.id,
                    'parent_classify_id': parent_classify_id,
                    'parent_classify_goods_classify': parent_classify_goods_classify,
                    'goods_classify': obj.goods_classify,
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S')
                })

            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': data_list,
                'data_count': objs.count()
            }
            response.note = {
                'id': '商品分类ID',
                'goods_classify': '商品分类名称',
                'create_datetime': '该商品分类创建时间',
                'parent_classify_goods_classify': '分类父级名称',
                'parent_classify_id': '分类父级ID',
            }
        else:
            response.code = 301
            response.msg = json.loads(forms_obj.errors.as_json())
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
