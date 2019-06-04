
from api import models
from publicFunc import account, Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from api.forms.admin.index_info import SelectForm
from django.db.models import Q, Count, Sum
import datetime, time, json


@csrf_exempt
def login(request):
    response = Response.ResponseObj()
    name = request.POST.get('name')
    password = request.POST.get('password')

    print(password)

    # 查询数据库
    userprofile_objs = models.Enterprise.objects.filter(
        name=name,
        password=account.str_encrypt(password),
        status=1 # 已审核
    )
    if userprofile_objs:
        # 如果有数据 查询第一条对象
        userprofile_obj = userprofile_objs[0]
        token = userprofile_obj.token
        # 如果没有token 则生成 token
        if not userprofile_obj.token:
            token = account.get_token(account.str_encrypt(password))
            userprofile_obj.token = token
        else:
            response.code = 200
            response.msg = '登录成功'
            time.time()

            response.data = {
                'token': token,
                'user_id': userprofile_obj.id,
                'name': userprofile_obj.name,
                'role': userprofile_obj.role,
                'phone': userprofile_obj.phone,
            }

        userprofile_obj.last_login_date = datetime.datetime.now()
        userprofile_obj.save()
    else:
        response.code = 401
        response.msg = "账号或密码错误"
    return JsonResponse(response.__dict__)



@csrf_exempt
@account.is_token(models.Enterprise)
def index_info(request, oper_type):
    response = Response.ResponseObj()

    form_obj = SelectForm(request.GET)
    if form_obj.is_valid():
        user_id, role = form_obj.cleaned_data.get('user_id') # 用户ID 用户角色
        now = datetime.datetime.today().strftime('%Y-%m-%d') # 当前时间 年月日

        # 数据概览
        if oper_type == 'overview_data':
            the_number_visitors_q = Q()             # 访客人数条件
            num_visitors_q = Q()                    # 访客次数条件
            number_people_placing_orders_q = Q()    # 下订单人数
            order_amount_q = Q()                    # 下订单金额

            if role == 1: # OEM
                the_number_visitors_q.add(Q(enterprise_id=user_id), Q.AND)
                num_visitors_q.add(Q(oper_user__enterprise_id=user_id), Q.AND)
                number_people_placing_orders_q.add(Q(create_user__enterprise_id=user_id), Q.AND)
                order_amount_q.add(Q(), Q.AND)


            # 访客人数查询
            the_number_visitors_objs = models.Userprofile.objects.filter(
                the_number_visitors_q,
                last_active_time__gte=now
            )

            # 访客次数查询
            num_visitors_objs = models.log_access.objects.filter(
                num_visitors_q,
                create_date__gte=now,

            )


            # 订单公共查询
            orders_objs = models.renewal_log.objects.select_related(
                'create_user'
            ).filter(
                number_people_placing_orders_q,
                create_date__gte=now
            )

            # 下订单人数
            number_people_placing_orders_objs = orders_objs.values('create_user').annotate(Count('create_user_id'))

            # 下订单金额
            order_amount_objs = orders_objs.aggregate(Sum('price'))


            the_number_visitors = the_number_visitors_objs.count()
            num_visitors = num_visitors_objs.count()
            number_people_placing_orders = number_people_placing_orders_objs.count()

            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'the_number_visitors': the_number_visitors,
                'num_visitors': num_visitors,
                'number_people_placing_orders': number_people_placing_orders,
                'order_amount': order_amount_objs.get('price__sum'),
            }

            response.note = {
                'the_number_visitors': '访客人数',
                'num_visitors': '访客次数',
                'number_people_placing_orders': '下订单人数',
                'order_amount': '下订单金额',
            }

        # 折线图
        elif oper_type == 'line_chart':
            days = request.GET.get('days') # 天数
            if days and days.isdigit():
                                # 遍历 ↓开始 ↓结束 ↓步长
                for day in range(int(days), 0, -1):
                    now_time = datetime.datetime.today()
                    pub_time = (now_time - datetime.timedelta(days=day - 1)).strftime("%Y-%m-%d")
                    start_time = pub_time + ' 00:00:00'
                    stop_time = pub_time + ' 23:59:59'

                    print('start_time, stop_time------------> ', start_time, stop_time)




            else:
                response.code = 301
                response.msg = '折线图异常'

        else:
            response.code = 402
            response.msg = '查询异常'

    else:
        response.code = 301
        response.msg = json.loads(form_obj.errors.as_json())

    return JsonResponse(response.__dict__)






