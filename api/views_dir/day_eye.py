from django.shortcuts import render
from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.day_eye import SelectForm, AddForm, UpdateForm
from django.db.models import Count, Sum
import json


# 放入开始和结束时间 返回 天 时 分 秒
def get_min_s(start_time=None, stop_time=None):
    date_time = stop_time - start_time
    day = date_time.days
    hour, date_time = divmod(date_time.seconds, 3600)
    min, date_time = divmod(date_time, 60)
    second =    date_time

    days = ''
    hours = ''
    mins = ''
    seconds = ''
    if day:
        days = str(day) + '天'
    if hour:
        hours = str(hour) + '小时'
    if min:
        mins = str(min) + '分钟'
        if second:
            mins = str(min) + '分'

    if second:
        seconds = str(second) + '秒'

    return days + hours + mins + seconds


# cerf  token验证 谁看了我(列表及详情)
@account.is_token(models.Userprofile)
def day_eye(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            user_id = forms_obj.cleaned_data['user_id']
            order = request.GET.get('order', '-create_datetime')
            customer = request.GET.get('customer_id')

            if not customer:  # 列表页
                objs = models.SelectArticleLog.objects.filter(
                    inviter_id=user_id
                ).select_related(
                    'customer'
                ).values(
                    'customer_id', 'customer__name'
                ).distinct().annotate(Count('customer_id'))

            else: # 详情页
                objs = models.SelectArticleLog.objects.filter(
                    inviter_id=user_id
                ).filter(customer_id=customer).order_by(order)

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]
            count = objs.count()

            # 返回的数据
            ret_data = []
            for obj in objs:
                if not customer: # 列表页
                    customer_id = obj.get('customer_id')
                    article_count = models.SelectArticleLog.objects.filter(
                        customer_id=customer_id,
                        inviter_id=user_id,
                    ).values('article_id').distinct().count()

                    ret_data.append({
                        'customer_id': customer_id,
                        'customer__name': obj.get('customer__name'),
                        'customer_id__count': obj.get('customer_id__count'), # 总共查看几次
                        'article_count': article_count,                      # 总共查看几篇文章
                    })

                else:
                    time_length = '1秒'
                    if obj.close_datetime:
                        time_length = get_min_s(obj.close_datetime, obj.create_datetime)
                    ret_data.append({
                        'id': obj.id,
                        'customer_id': obj.customer_id,
                        'customer__name': obj.customer.name,
                        'article_id': obj.article_id,
                        'article__title': obj.article.title,
                        'time_length':time_length,
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
                'customer_id': "查看人ID",
                'customer__name': "查看人姓名",
                'article_id': "文章ID",
                'article__title': "文章标题",
                'close_datetime': "关闭页面时间",
                'create_datetime': "创建时间",
                '--------以下为列表页查询数据--------':'',
                'customer_id__count':'总共查看几次',
                'article_count':'总共查看几篇文章',
            }
        else:
            print("forms_obj.errors -->", forms_obj.errors)
            response.code = 402
            response.msg = "请求异常"
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)


# 增删改
# token验证
@account.is_token(models.Userprofile)
def day_eye_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')

    if request.method == "POST":
        form_data = {
            'o_id':o_id,
            'user_id':user_id,
            'customer_id': request.POST.get('customer_id'),
            'remote_type': request.POST.get('remote_type'),
            'title': request.POST.get('title'),
            'create_date': request.POST.get('create_date'),
            'remote': request.POST.get('remote')
        }

        # 添加客户信息备注
        if oper_type == "add":
            form_obj = AddForm(form_data)
            if form_obj.is_valid():
                remote_type = form_obj.cleaned_data.get('remote_type')
                title = form_obj.cleaned_data.get('title')
                remote = form_obj.cleaned_data.get('remote')
                customer_id = form_obj.cleaned_data.get('customer_id')
                create_date = form_obj.cleaned_data.get('create_date')

                if remote_type == 2:
                    remote_text = {'create_date':create_date, 'title':title, 'remote':remote}

                elif remote_type == 3:
                    remote_text = {'title':title, 'remote':remote}

                else:
                    remote_text = {'remote':remote}

                data = {
                    'user_id':user_id,
                    'customer_id':customer_id,
                    'remote_type':remote_type,
                    'remote':remote_text
                }
                models.customer_information_the_user.objects.create(**data)
                response.code = 200
                response.msg = '保存成功'

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 修改客户信息备注
        elif oper_type == 'update':
            form_obj = UpdateForm(form_data)
            if form_obj.is_valid():
                o_id, remote_type = form_obj.cleaned_data.get('o_id')
                title = form_obj.cleaned_data.get('title')
                remote = form_obj.cleaned_data.get('remote')
                create_date = form_obj.cleaned_data.get('create_date')

                if remote_type == 2:
                    remote_text = {'create_date':create_date, 'title':title, 'remote':remote}

                elif remote_type == 3:
                    remote_text = {'title':title, 'remote':remote}

                else:
                    remote_text = {'remote':remote}

                models.customer_information_the_user.objects.filter(id=o_id).update(
                    remote=remote_text
                )
                response.code = 200
                response.msg = '保存成功'

            else:
                response.code = 301
                response.msg = json.loads(form_obj.errors.as_json())

        # 删除客户信息备注
        elif oper_type == 'delete':
            objs = models.customer_information_the_user.objects.filter(id=o_id)
            if not objs:
                response.code = 301
                response.msg = '刪除数据不存在'
            else:
                objs.delete()
                response.code = 200
                response.msg = '删除成功'

    else:

        # 查询客户信息备注
        if oper_type == 'get_customer_note':
            pass

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)
