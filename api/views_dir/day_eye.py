from api import models
from publicFunc import Response
from publicFunc import account
from django.http import JsonResponse
from publicFunc.condition_com import conditionCom
from api.forms.day_eye import SelectForm, AddForm, UpdateForm
from django.db.models import Count
from publicFunc.base64_encryption import b64decode, b64encode
import datetime, json


# 放入开始和结束时间 返回 天 时 分 秒
def get_min_s(start_time=None, stop_time=None, ms=None):
    date_time = stop_time - start_time
    day = date_time.days
    hour, date_time = divmod(date_time.seconds, 3600)
    min, date_time = divmod(date_time, 60)
    second = date_time
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
    if ms:
        if days or hours:
            if days and int(days.split('天')[0]) >= 365:
                return '一年'
            if not hours:
                return days
            elif not days:
                return hours
            else:
                return days + hours
        else:
            return mins + seconds
    else:
        if days:
            if int(days.split('天')[0]) >= 365:
                return '一年'
        return days + hours + mins + seconds


# cerf  token验证 谁看了我(列表)
@account.is_token(models.Userprofile)
def day_eye(request):
    response = Response.ResponseObj()
    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']
            user_id, message = forms_obj.cleaned_data['user_id']

            objs = models.day_eye_celery.objects.filter(
                user_id=user_id
            ).order_by(
                '-create_date'
            )
            count = objs.count()

            if length != 0:
                start_line = (current_page - 1) * length
                stop_line = start_line + length
                objs = objs[start_line: stop_line]

            ret_data = []
            data_list = []
            for obj in objs:
                if obj.customer_id not in data_list:
                    data_list.append(obj.customer_id)
            for customer_id in data_list:
                eye_objs = models.day_eye_celery.objects.filter(user_id=user_id, customer_id=customer_id).order_by('-create_date')
                flag = False
                for eye_obj in eye_objs:
                    if eye_obj.is_new_msg:
                        flag = True

                obj = eye_objs[0]
                ret_data.append({
                    'customer_id': obj.customer_id,
                    'customer__name': b64decode(obj.customer.name),
                    'customer__set_avator': obj.customer.set_avator,
                    'text': obj.text,
                    'status': obj.status,
                    'is_new_msg': flag,
                })

            #  查询成功 返回200 状态码
            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'ret_data': ret_data,
                'count': count,
                'message': message,
            }
            response.note = {
                'customer_id': "查看人ID",
                'customer__name': "查看人姓名",
                'customer__set_avator': '客户头像',
                'text': '显示的文字',
                'status': '区分 文章还是商品',
                'message': '展示的文字/判断是否为空 为空不显示',
            }
        else:
            print("forms_obj.errors -->", forms_obj.errors)
            response.code = 301
            response.data = json.loads(forms_obj.errors.as_json())
    return JsonResponse(response.__dict__)

# 增删改
# token验证
@account.is_token(models.Userprofile)
def day_eye_oper(request, oper_type, o_id):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    forms_obj = SelectForm(request.GET)
    if forms_obj.is_valid():
        current_page = forms_obj.cleaned_data['current_page']
        length = forms_obj.cleaned_data['length']
        order = request.GET.get('order', '-create_datetime')
        if request.method == "POST":
            form_data = {
                'o_id': o_id,
                'user_id': user_id,
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
                    remote = form_obj.cleaned_data.get('remote')
                    customer_id = form_obj.cleaned_data.get('customer_id')

                    data = {
                        'user_id': user_id,
                        'customer_id': customer_id,
                        'remote': remote
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
                    o_id = form_obj.cleaned_data.get('o_id')
                    remote = form_obj.cleaned_data.get('remote')

                    models.customer_information_the_user.objects.filter(id=o_id).update(
                        remote=remote
                    )
                    response.code = 200
                    response.msg = '保存成功'

                else:
                    response.code = 301
                    response.msg = json.loads(form_obj.errors.as_json())

            # 删除客户信息备注
            elif oper_type == 'delete':
                customer_id = request.POST.get('customer_id')

                if customer_id:
                    objs = models.customer_information_the_user.objects.filter(
                        user_id=user_id,
                        customer_id=customer_id
                    )
                else:
                    objs = models.customer_information_the_user.objects.filter(id=o_id)

                if not objs:
                    response.code = 301
                    response.msg = '刪除数据不存在'
                else:
                    objs.delete()
                    response.code = 200
                    response.msg = '删除成功'


            # 添加客户资料
            elif oper_type == 'add_customer_info':
                pass

            # 修改客户资料 个人信息等
            elif oper_type == 'update_customer_info':
                print('request.POST=============================000000000-=-------------> ', request.POST)
                customer_info = request.POST.get('customer_info')
                objs = models.user_comments_customer_information.objects.filter(
                    user_id=user_id,
                    customer_id=o_id
                )
                print('request.POST=============================000000000-=-------------> ', type(customer_info), customer_info)
                customer_info = eval(customer_info)

                if objs:
                    objs.update(customer_info=json.dumps(customer_info))
                else:
                    objs.create(
                        customer_info=customer_info,
                        user_id=user_id,
                        customer_id=o_id
                    )
                response.code = 200
                response.msg = '保存成功'
                response.note = {
                    'customer_info':'用户所有信息',
                    'customer_sex': '用户性别 默认微信性别',
                    'customer_set_avator': '用户头像 默认微信头像',
                    'customer_name': '用户姓名 备注 默认微信名称',
                    'customer_wechat': '用户微信名称',
                    'customer_phone': '用户电话',
                    'customer_professional': '用户职业',
                    'customer_birthday': '用户生日',
                    'customer_remake': '用户备注',
                    'customer_demand': '用户需求',
                    'customer_label': {
                        'xueli':'学历ID',
                        'diqu':'地区名称',
                        'guanxi':'关系',
                        'qinmidu':'亲密度',
                        'yingxiangli':'影响力',
                        'qituxin':'企图心',
                        'shiyetaidu':'事业态度',
                        'renmaiquan':'人脉圈',
                        'jingjinengli':'经济能力',
                    },
                }

        else:

            # 查询客户信息备注
            if oper_type == 'get_customer_note':
                field_dict = {
                    'id': '',
                    'customer_id': '',
                    'user_id': '',
                }

                q = conditionCom(request, field_dict)
                objs = models.customer_information_the_user.objects.filter(q).order_by(order)

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]
                count = objs.count()

                ret_data = []
                num = 0
                for obj in objs:
                    create_datetime = obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S')
                    ret_data.append({
                        'create_datetime': create_datetime
                    })
                    ret_data[num]['remote'] = obj.remote
                    ret_data[num]['id'] = obj.id
                    num += 1

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'count': count,
                    'ret_data': ret_data,
                }

                response.note = {
                    'create_datetime':'创建时间',
                    'remote':'备注',
                }

            # 谁看了我 (文章详情)
            elif oper_type == 'day_eye_detail':
                user_id = forms_obj.cleaned_data['user_id']

                # 更新 用户点击客户详情时间
                day_celery_objs = models.day_eye_celery.objects.filter(status=1, user_id=user_id, customer_id=o_id)
                if day_celery_objs:
                    day_celery_objs.update(
                        last_click_customer=datetime.datetime.today(),
                        is_new_msg=False
                    )

                article_objs = models.SelectArticleLog.objects.filter(inviter_id=user_id, customer_id=o_id)
                info_objs = article_objs.order_by(order)

                objs = article_objs.values('article_id', 'article__title', 'article__cover_img').annotate(Count('id'))
                count = objs.count()

                ret_data = []
                for obj in objs:
                    article_id = obj.get('article_id')
                    article_obj = article_objs.filter(article_id=article_id).order_by(order)[:1]

                    time_detail = []    # 查看时长及时间
                    for info_obj in info_objs:
                        if int(info_obj.article_id) == int(article_id):
                            time_length = '1秒'
                            create_datetime = info_obj.create_datetime
                            if info_obj.close_datetime:
                                time_length = get_min_s(create_datetime, info_obj.close_datetime)
                            time_detail.append({
                                'time_length': time_length,
                                'select_datetime': create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                            })

                    create_datetime = article_obj[0].create_datetime
                    after_time = get_min_s(create_datetime, datetime.datetime.today(), ms=1)

                    ret_data.append({
                        'article_id': article_id,
                        'article__title': obj.get('article__title'),
                        'article_info': '看了' + str(obj.get('id__count')) + '次-' +  after_time + '前',
                        'time_detail': time_detail,
                        'article__cover_img': obj.get('article__cover_img'),
                        'create_datetime': create_datetime, # 排序用
                    })
                data_list = sorted(ret_data, key=lambda x: x['create_datetime'], reverse=True)

                is_new_goods_msg = False
                goods_objs = models.day_eye_celery.objects.filter(status=2, user_id=user_id, customer_id=o_id)
                if goods_objs:
                    if goods_objs[0].is_new_msg:
                        is_new_goods_msg = True

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': data_list,
                    'data_count': count,
                    'is_new_goods_msg': is_new_goods_msg,
                }
                response.note = {
                    'article_id': "文章ID",
                    'article__title': "文章标题",
                    'article_info': "看了几次 最后一次查看时间",
                    'time_length': "时长",
                    'select_datetime': "查看时间",
                    'article__cover_img': "文章图片",
                    'create_datetime': "创建时间",
                    'is_new_goods_msg': "是否有商品新消息",
                }

            # 按文章查看(天眼功能)列表页
            elif oper_type == 'view_by_article':
                user_id, message = forms_obj.cleaned_data['user_id']
                objs = models.SelectArticleLog.objects.filter(
                    inviter_id=user_id
                ).values('article_id', 'article__title').distinct().annotate(Count('id')).exclude(customer_id__isnull=True)
                count = objs.count()

                ret_data = []
                for obj in objs:
                    article_obj = models.SelectArticleLog.objects.filter(article_id=obj['article_id']).order_by(order)
                    cover_img = article_obj[0].article.cover_img    # 文章封面
                    create_datetime = article_obj[0].create_datetime
                    after_time = get_min_s(create_datetime, datetime.datetime.today(), ms=1)

                    ret_data.append({
                        'article_id': obj['article_id'],
                        'article__title': obj['article__title'],
                        'id__count': obj['id__count'],
                        'after_time': after_time + '前',
                        'cover_img': cover_img + '?imageView2/2/w/200',
                        'create_datetime': create_datetime,
                    })

                ret_data = sorted(ret_data, key=lambda x: x['create_datetime'], reverse=True)
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    ret_data = ret_data[start_line: stop_line]

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count,
                    'message': message,
                }
                response.note = {
                    'article_id': '文章ID',
                    'article__title': '文章标题',
                    'id__count': '查看该文章人 总数',
                    'cover_img': '文章封面',
                    'after_time': '最后查看日期',
                }

            # 按文章查看(详情)
            elif oper_type == 'view_by_article_detail':
                article_obj = models.SelectArticleLog.objects.filter(
                    inviter_id=user_id,
                    article_id=o_id,
                    customer_id__isnull=False
                )
                objs = article_obj.values('customer_id', 'customer__name', 'customer__set_avator').distinct().annotate(Count('id'))

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]
                count = objs.count()
                ret_data = []
                for obj in objs:
                    objs = article_obj.filter(customer_id=obj['customer_id'])[:1]
                    create_datetime = objs[0].create_datetime
                    after_time = get_min_s(create_datetime, datetime.datetime.today(), ms=1)
                    ret_data.append({
                        'customer_id': obj['customer_id'],
                        'customer__set_avator': obj['customer__set_avator'] + '?imageView2/2/w/200',
                        'customer__name': b64decode(obj['customer__name']),
                        'article_info': '看了' + str(obj['id__count']) + '次-' + after_time + '前',
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data': ret_data,
                    'count': count,
                }
                response.note = {
                    'customer_id': '客户ID',
                    'customer__name': '客户名称',
                    'article_info': '该人查看该文章 总数/ 时长',
                }

            # 查询客户资料
            elif oper_type == 'get_customer_info':
                objs = models.user_comments_customer_information.objects.filter(
                    user_id=user_id,
                    customer_id=o_id
                )

                if not objs:
                    customer_info = {
                        'customer_sex': '',
                        'customer_set_avator': '',
                        'customer_name': '',
                        'customer_wechat': '',
                        'customer_phone': '',
                        'customer_professional': '',
                        'customer_birthday': '',
                        'customer_remake': '',
                        'customer_demand': [],
                        'customer_label': {
                            'xueli': '初中',
                            'diqu': '北京',
                            'guanxi': '朋友',
                            'qinmidu': 1,
                            'yingxiangli': 1,
                            'qituxin': 1,
                            'shiyetaidu': 1,
                            'renmaiquan': 1,
                            'jingjinengli': 1,
                        },
                    }
                    models.user_comments_customer_information.objects.create(
                        user_id=user_id,
                        customer_id=o_id,
                        customer_info=customer_info
                    )

                    objs = models.user_comments_customer_information.objects.filter(
                        user_id=user_id,
                        customer_id=o_id
                    )

                obj = objs[0]
                info = eval(obj.customer_info)

                customer_sex = obj.customer.sex
                if info.get('customer_sex'):
                    customer_sex = info.get('customer_sex')

                customer_set_avator = obj.customer.set_avator
                if info.get('customer_set_avator'):
                    customer_set_avator = info.get('customer_set_avator')

                customer = b64decode(obj.customer.name)
                customer_name = customer
                if info.get('customer_name'):
                    customer_name = info.get('customer_name')

                customer_label = info.get('customer_label')
                print('customer_label-------> ', customer_label)
                try:
                    customer_demand = eval(info.get('customer_demand'))
                except Exception:
                    customer_demand = info.get('customer_demand')

                ret_data = {
                    'customer_sex': customer_sex,
                    'customer_set_avator': customer_set_avator,
                    'customer_name': customer_name,
                    'customer_wechat': customer,
                    'customer_phone': info.get('customer_phone'),
                    'customer_professional': info.get('customer_professional'),
                    'customer_birthday': info.get('customer_birthday'),
                    'customer_remake': info.get('customer_remake'),
                    'customer_demand': customer_demand,
                    'customer_label': {
                        'xueli': customer_label.get('xueli'),
                        'diqu': customer_label.get('diqu'),
                        'guanxi': customer_label.get('guanxi'),
                        'qinmidu': customer_label.get('qinmidu'),
                        'yingxiangli': customer_label.get('yingxiangli'),
                        'qituxin': customer_label.get('qituxin'),
                        'shiyetaidu': customer_label.get('shiyetaidu'),
                        'renmaiquan': customer_label.get('renmaiquan'),
                        'jingjinengli': customer_label.get('jingjinengli'),
                    },
                    'create_datetime': obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S')
                }

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'ret_data':ret_data
                }
                response.note = {
                    'customer_sex': '用户性别 默认微信性别',
                    'customer_set_avator': '用户头像 默认微信头像',
                    'customer_name': '用户姓名 备注 默认微信名称',
                    'customer_wechat': '用户微信名称',
                    'customer_phone': '用户电话',
                    'customer_professional': '用户职业',
                    'customer_birthday': '用户生日',
                    'customer_remake': '用户备注',
                    'customer_demand': '用户需求',
                    'customer_label': {
                        'xueli':'学历ID',
                        'diqu':'地区名称',
                        'guanxi':'关系',
                        'qinmidu':'亲密度',
                        'yingxiangli':'影响力',
                        'qituxin':'企图心',
                        'shiyetaidu':'事业态度',
                        'renmaiquan':'人脉圈',
                        'jingjinengli':'经济能力',
                    }
                }

            # 查看客户详情(客户信息)
            elif oper_type == 'info_detail':
                # info_objs = models.SelectArticleLog.objects.filter(inviter_id=user_id, customer_id=o_id).order_by(order)
                # 谁看了我详情 右上角星星数据
                info_data = {
                    'xueli': '初中',
                    'diqu': '北京',
                    'guanxi': '朋友',
                    'qinmidu': 1,
                    'yingxiangli': 1,
                    'qituxin': 1,
                    'shiyetaidu': 1,
                    'renmaiquan': 1,
                    'jingjinengli': 1,
                    'customer_demand':[]
                }
                information_objs = models.user_comments_customer_information.objects.filter(user_id=user_id, customer_id=o_id)
                if information_objs:
                    information_obj = information_objs[0]
                    try:
                        customer_info = eval(information_obj.customer_info)
                    except Exception:
                        customer_info = information_obj.customer_info
                    customer_label = customer_info.get('customer_label')

                    try:
                        customer_demand = json.loads(customer_info.get('customer_demand'))
                    except Exception:
                        customer_demand = customer_info.get('customer_demand')

                    info_data = {
                        'xueli': customer_label.get('xueli'),
                        'diqu': customer_label.get('diqu'),
                        'guanxi': customer_label.get('guanxi'),
                        'qinmidu': customer_label.get('qinmidu'),
                        'yingxiangli': customer_label.get('yingxiangli'),
                        'qituxin': customer_label.get('qituxin'),
                        'shiyetaidu': customer_label.get('shiyetaidu'),
                        'renmaiquan': customer_label.get('renmaiquan'),
                        'jingjinengli': customer_label.get('jingjinengli'),
                        'customer_demand': customer_demand,
                    }
                avg_stars_list = []
                for k, v in info_data.items():
                    if k in ['qinmidu', 'yingxiangli', 'qituxin', 'shiyetaidu', 'renmaiquan', 'jingjinengli']:
                        avg_stars_list.append(int(v))
                avg_stars = sum(avg_stars_list) / 6  # 右上角星星 平均值

                obj = models.Customer.objects.get(id=o_id)
                # 客户基本信息
                customer_info = {
                    'customer_id': obj.id,
                    'customer__name': b64decode(obj.name),
                    'customer__set_avator': obj.set_avator,
                    'info_data': info_data,
                    'avg_stars': avg_stars,
                }

                is_remake_count = models.customer_information_the_user.objects.filter(
                    user_id=user_id,
                    customer_id=o_id
                ).count()
                is_remake = False
                if is_remake_count >= 1:
                    is_remake = True

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'customer_info': customer_info,
                    'is_remake': is_remake
                }
                response.note = {
                    'customer_id': "客户id",
                    'customer__name': "客户姓名",
                    'customer__set_avator': "客户头像",
                    'is_remake': "该客户是否有备注(如果有那么可删除)",
                    'qinmidu': '亲密度',
                    'yingxiangli': '影响力',
                    'qituxin': '企图心',
                    'shiyetaidu': '事业态度',
                    'renmaiquan': '人脉圈',
                    'jingjinengli': '经济能力',
                    'avg_stars': '星星平均值',
                }

            # 谁看了我(商品详情)
            elif oper_type == 'day_eye_goods_detail':
                # 更新 用户点击客户详情时间
                day_celery_objs = models.day_eye_celery.objects.filter(status=2, user_id=user_id, customer_id=o_id)
                if day_celery_objs:
                    day_celery_objs.update(last_click_customer=datetime.datetime.today(), is_new_msg=False)

                objs = models.customer_look_goods_log.objects.filter(
                    user_id=user_id,
                    customer_id=o_id
                ).select_related('goods').values(
                    'goods_id',
                    'goods__cover_img',
                    'goods__goods_name',
                ).annotate(Count('id'))

                data_list = []
                for obj in objs:
                    goods_id = obj.get('goods_id')
                    detail_objs = models.customer_look_goods_log.objects.filter(
                        user_id=user_id,
                        customer_id=o_id,
                        goods_id=goods_id
                    ).order_by('-create_datetime')

                    time_detail = []
                    for detail_obj in detail_objs: # 详情
                        time_length = '1秒'
                        if detail_obj.close_datetime:
                            time_length = get_min_s(detail_obj.create_datetime, detail_obj.close_datetime)

                        time_detail.append({
                            'create_datetime': detail_obj.create_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                            'time_length': time_length
                        })
                    create_datetime = detail_objs[0].create_datetime
                    time_length = get_min_s(create_datetime, datetime.datetime.today())
                    data_list.append({
                        'goods_id': goods_id,
                        'goods__cover_img': obj.get('goods__cover_img'),
                        'goods__goods_name': obj.get('goods__goods_name'),
                        'text':'看了{}次-{}前'.format(
                            obj.get('id__count'),
                            time_length
                        ),
                        'time_detail':time_detail,
                        'create_datetime': create_datetime
                    })
                    data_list = sorted(data_list, key=lambda x: x['create_datetime'], reverse=True)
                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'data_list': data_list
                }

            else:
                response.code = 402
                response.msg = '请求异常'

    else:
        response.code = 301
        response.msg = json.loads(forms_obj.errors.as_json())

    return JsonResponse(response.__dict__)

