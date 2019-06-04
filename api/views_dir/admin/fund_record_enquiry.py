from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Q
import json, datetime, time



@csrf_exempt
@account.is_token(models.Enterprise)
def fund_record_enquiry_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    pub_user_obj = models.Enterprise.objects.get(id=user_id)
    role = int(pub_user_obj.role)

    if request.method == "GET":


        # 总资金记录
        if oper_type == 'total_fund_record':
            q = Q()
            if role == 1:
                q.add(Q(create_user__enterprise_id=user_id), Q.AND)

            pub_objs = models.renewal_log.objects.filter(
                q,
                isSuccess=1
            )

            dingdan_id_list = [i.id for i in pub_objs]


            dingdan_num = pub_objs.count() # 订单总数







        # 销售数据
        elif oper_type == '':
            print('-')


        # 提现数据
        elif oper_type == '':
            print('=')


    else:
        if oper_type == '':
            print('--')

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)




