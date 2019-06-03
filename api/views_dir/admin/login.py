
from api import models
from publicFunc import account, Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import datetime, time

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
    user_id = request.GET.get('user_id')

    # 数据概览
    if oper_type == 'overview_data':
        now = datetime.datetime.today().strftime('%Y-%m-%d')

        objs = models.Userprofile.objects.filter(
            enterprise_id=user_id,
            last_active_time__gte=now
        )

        number_visitors = objs.count()


    else:
        print('--')








