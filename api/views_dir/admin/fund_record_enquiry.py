from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Q, Sum
from publicFunc.base64_encryption import b64decode
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

            # 续费记录
            renewal_objs = models.renewal_log.objects.filter(
                create_user__enterprise_id=user_id,
                isSuccess=1
            )

            # 提现记录
            withdrawal_amount_objs = models.withdrawal_log.objects.filter(
                user__enterprise_id=user_id,
                is_success=1
            )

            # 一级分成钱数
            one_division_money = models.distribute_money_log.objects.filter(
                inviter__enterprise_id=user_id,
                status=1
            ).aggregate(Sum('money')).get('money__sum')

            # 二级分成钱数
            two_division_money = models.distribute_money_log.objects.filter(
                inviter__enterprise_id=user_id,
                status=2
            ).aggregate(Sum('money')).get('money__sum')

            total_amount_renewal = renewal_objs.aggregate(Sum('price')).get('price__sum') # 续费总金额
            total_withdrawal_amount = withdrawal_amount_objs.aggregate(Sum('withdrawal_amount')).get('withdrawal_amount__sum') # 提现总金额
            total_amount_funds = total_withdrawal_amount + total_amount_renewal # 资金总额
            total_number_orders = renewal_objs.count() + withdrawal_amount_objs.count() # 订单总数

            renewal_list = []
            for renewal_obj in renewal_objs:
                renewal_list.append({
                    'consumption_type':'充值会员',
                    'consumer_user': b64decode(renewal_obj.create_user.name),
                    'create_date': renewal_obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'price':renewal_obj.price
                })

            withdrawal_amount_list = []
            for withdrawal_amount_obj in withdrawal_amount_objs:
                withdrawal_amount_list.append({
                    'consumption_type': '提现',
                    'consumer_user': b64decode(withdrawal_amount_obj.user.name),
                    'create_date': withdrawal_amount_obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'price': withdrawal_amount_obj.withdrawal_amount
                })

            renewal_list.extend(withdrawal_amount_list)
            data_list = sorted(renewal_list, key=lambda x: x['create_date'], reverse=True)

            data_dict = {
                'total_amount_funds': total_amount_funds,
                'total_number_orders': total_number_orders,
                'one_division_money': one_division_money,
                'two_division_money': two_division_money,
                'data_list': data_list,
            }

            ret_data = {}
            for k, v in data_dict.items():
                if v is None:
                    v = 0
                ret_data[k]=v

            response.code = 200
            response.msg = '查询成功'
            response.data = ret_data
            response.note = {
                'total_amount_funds': '资金总额',
                'total_number_orders': '订单总数',
                'one_division_money': '一级分成钱数',
                'two_division_money': '二级分成钱数',
                'data_list': [
                    {
                        'consumption_type':'消费类型',
                        'consumer_user': '消费用户',
                        'create_date': '消费时间',
                        'price': '消费金额'
                    },
                ],
            }

        # 销售数据
        elif oper_type == 'sales_data':

            objs = models.distribute_money_log.objects.filter(
                inviter__enterprise_id=user_id
            )
            total_number_orders = objs.count() # 总订单
            primary_distribution_orders = objs.filter(status=1).count() # 一级订单
            Secondary_distribution_orders = objs.filter(status=2).count() # 二级订单

            data_list = []
            for obj in objs:
                data_list.append({
                    'distribution_level': obj.get_status_display(),
                    'name': b64decode(obj.user.name),
                    'money': obj.money,
                    'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                })

            ret_data = {
                'total_number_orders': total_number_orders,
                'primary_distribution_orders': primary_distribution_orders,
                'Secondary_distribution_orders': Secondary_distribution_orders,
                'data_list': data_list,
            }

            response.code = 200
            response.msg = '查询成功'
            response.data = ret_data
            response.note = {
                'total_number_orders': '总订单',
                'primary_distribution_orders': '一级订单',
                'Secondary_distribution_orders': '二级订单',
                'data_list': [
                    {
                        'distribution_level': '分销级别',
                        'name': '分销人名称',
                        'money': '分销金额',
                        'create_date': '创建时间',
                    }
                ],
            }

        # 提现数据
        elif oper_type == 'withdrawal_data':
            objs = models.withdrawal_log.objects.filter(
                user__enterprise_id=user_id,
                is_success=1
            )
            total_amount_withdrawal = objs.count()

            data_list = []
            for obj in objs:
                is_success = '提现失败'
                if obj.is_success:
                    is_success = '提现成功'

                data_list.append({
                    'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'withdrawal_befor': obj.withdrawal_befor,   # 提现前 余额
                    'withdrawal_amount': obj.withdrawal_amount, # 提现 金额
                    'withdrawal_after': obj.withdrawal_after,   # 提现后 余额
                    'is_success': is_success,
                    'wechat_returns_data': obj.wechat_returns_data,
                    'name': b64decode(obj.user.name),
                    'order_number': obj.dingdanhao
                })

            response.code = 200
            response.msg = '查询成功'
            response.data = {
                'total_amount_withdrawal': total_amount_withdrawal,
                'data_list': data_list
            }
            response.note = {
                'total_amount_withdrawal': '销售总额',
                'data_list': [
                    {
                        'create_date': '提现时间',
                        'withdrawal_befor': '提现前 余额',
                        'withdrawal_amount': '提现 金额',
                        'withdrawal_after': '提现后 余额',
                        'is_success': '是否成功',
                        'wechat_returns_data': '失败原因',
                        'name': '提现人名称',
                        'order_number': '提现订单号'
                    }
                ]
            }

    else:
        if oper_type == '':
            print('--')

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)




