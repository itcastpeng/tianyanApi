from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse

from publicFunc.condition_com import conditionCom
from api.forms.small_shop import AddForm, UpdateForm, SelectForm, AddGoodForm, UpdateGoodForm, DeleteGoodForm
import json


# token验证 微店展示模块
# @account.is_token(models.Userprofile)
def small_shop(request):
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
                'goods_classify__oper_user_id': '',  # 查看的谁的微店
                'goods_classify_id': '',
                'goods_name': '__contains',
                'create_datetime': '',
                'goods_status': '',
            }
            q = conditionCom(request, field_dict)

            print('q -->', q)
            objs = models.Goods.objects.filter(q).order_by(order)
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
                    'goods_classify_id': obj.goods_classify_id,             # 分类ID
                    'goods_classify': obj.goods_classify.goods_classify,    # 分类名称
                    'goods_name': obj.goods_name,                           # 商品名称
                    'price': obj.price,                                     # 商品价格
                    'inventory': obj.inventory,                             # 商品库存
                    'freight': obj.freight,                                 # 商品运费
                    'goods_describe': obj.goods_describe,                   # 商品描述
                    'point_origin': obj.point_origin,                       # 商品发货地
                    'goods_status_id': obj.goods_status,                    # 商品状态ID
                    'goods_status': obj.get_goods_status_display(),         # 商品状态
                    'goods_picture': obj.goods_picture,                     # 商品图片
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
                'id': "文章id",
                'goods_classify':'商品分类',
                'goods_name':'分类名称',
                'price':'商品价格',
                'inventory':'商品库存',
                'freight':'商品运费',
                'goods_describe':'商品描述',
                'point_origin':'商品发货地',
                'goods_status':'商品状态',
                'goods_picture':'商品图片',
                'create_datetime':'商品创建时间',
            }
        else:
            response.code = 301
            response.data = json.loads(forms_obj.errors.as_json())
    else:
        response.code = 402
        response.msg = "请求异常"
    return JsonResponse(response.__dict__)


# 微店增删改
# token验证
@account.is_token(models.Userprofile)
def small_shop_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    if request.method == "POST":

        # 修改微店 静态横图
        if oper_type == "static_image":
            pass

        # 添加商品分类
        elif oper_type == "add_classify":
            form_data = {
                'oper_user_id': user_id,
                'goods_classify': request.POST.get('goods_classify'),
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
                'o_id':o_id,
                'oper_user_id': user_id,
                'goods_classify': request.POST.get('goods_classify'),
            }

            forms_obj = UpdateForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                o_id, objs = forms_obj.cleaned_data['o_id']
                goods_classify = forms_obj.cleaned_data['goods_classify']

                #  查询更新 数据
                objs.update(
                    goods_classify=goods_classify,
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

        # 添加商品
        elif oper_type == "add_good":
            form_data = {
                'create_user_id': user_id,
                'goods_classify_id': request.POST.get('goods_classify_id'), # 商品分类
                'goods_name': request.POST.get('goods_name'),               # 商品名称
                'price': request.POST.get('price'),                         # 商品价格
                'inventory': request.POST.get('inventory'),                 # 库存
                'freight': request.POST.get('freight', 0),                  # 运费
                'goods_describe': request.POST.get('goods_describe'),       # 商品描述
                'point_origin': request.POST.get('point_origin'),           # 发货地
                'goods_status': request.POST.get('goods_status', 2),        # 商品状态
                'goods_picture': request.POST.get('goods_picture'),         # 商品图片
            }
            print('form_data-------> ', form_data)

            forms_obj = AddGoodForm(form_data)
            if forms_obj.is_valid():
                print("验证通过")
                form_obj = forms_obj.cleaned_data
                obj = models.Goods.objects.create(**{
                    'goods_classify_id':form_obj.get('goods_classify_id'),
                    'goods_name':form_obj.get('goods_name'),
                    'price':form_obj.get('price'),
                    'inventory':form_obj.get('inventory'),
                    'freight':form_obj.get('freight'),
                    'goods_describe':form_obj.get('goods_describe'),
                    'point_origin':form_obj.get('point_origin'),
                    'goods_status':form_obj.get('goods_status'),
                    'goods_picture':form_obj.get('goods_picture')
                })
                response.code = 200
                response.msg = "添加成功"
                response.data = {'id': obj.id}
            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 修改商品
        elif oper_type == "update_good":
            form_data = {
                'o_id':o_id,
                'create_user_id': user_id,
                'goods_classify_id': request.POST.get('goods_classify_id'),     # 商品分类
                'goods_name': request.POST.get('goods_name'),                   # 商品名称
                'price': request.POST.get('price'),                             # 商品价格
                'inventory': request.POST.get('inventory'),                     # 库存
                'freight': request.POST.get('freight', 0),                      # 运费
                'goods_describe': request.POST.get('goods_describe'),           # 商品描述
                'point_origin': request.POST.get('point_origin'),               # 发货地
                'goods_status': request.POST.get('goods_status', 2),            # 商品状态
                'goods_picture': request.POST.get('goods_picture'),             # 商品图片
            }

            forms_obj = UpdateGoodForm(form_data)
            if forms_obj.is_valid():
                print('验证通过')
                form_obj = forms_obj.cleaned_data
                models.Goods.objects.filter(id=o_id).update(**{
                    'goods_classify_id': form_obj.get('goods_classify_id'),
                    'goods_name': form_obj.get('goods_name'),
                    'price': form_obj.get('price'),
                    'inventory': form_obj.get('inventory'),
                    'freight': form_obj.get('freight'),
                    'goods_describe': form_obj.get('goods_describe'),
                    'point_origin': form_obj.get('point_origin'),
                    'goods_status': form_obj.get('goods_status'),
                    'goods_picture': form_obj.get('goods_picture')
                })
                response.code = 200
                response.msg = "修改成功"

            else:
                print("验证不通过")
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        # 删除商品
        elif oper_type == "delete_good":
            objs = models.Goods.objects.filter(id=o_id)
            if objs:
                objs.delete()
                response.code = 200
                response.msg = "删除成功"
            else:
                response.code = 302
                response.msg = '删除ID不存在'

    else:

        # 查询商品分类
        if oper_type == 'get_goods_classify':
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
                    data_list.append({
                        'id':obj.id,
                        'goods_classify':obj.goods_classify,
                        'create_datetime':obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S')
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = data_list
                response.note = {
                    'id':'商品分类ID',
                    'goods_classify':'商品分类名称',
                    'create_datetime':'该商品分类创建时间'
                }
            else:
                response.code = 301
                response.msg = json.loads(forms_obj.errors.as_json())

        else:
            response.code = 402
            response.msg = "请求异常"

    return JsonResponse(response.__dict__)
