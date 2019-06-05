from api import models
from publicFunc import Response, account
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Q, Sum
from publicFunc.base64_encryption import b64decode
from api.forms.admin.fund_record_enquiry import SelectForm
import json, datetime, time


# 充值会员 数据 (续费)
def purchase_membership(objs):
    renewal_list = []
    for obj in objs:
        renewal_list.append({
            'consumption_type': '充值会员',
            'consumer_user': b64decode(obj.create_user.name),
            'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            'price': obj.price,
            'order_number': obj.pay_order_no
        })
    return renewal_list

# 提现 数据
def withdrawal(objs):
    withdrawal_amount_list = []
    for obj in objs:
        withdrawal_amount_list.append({
            'consumption_type': '提现',
            'consumer_user': b64decode(obj.user.name),
            'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
            'price': obj.withdrawal_amount,
            'order_number': obj.dingdanhao
        })
    return withdrawal_amount_list



@csrf_exempt
@account.is_token(models.Enterprise)
def fund_record_enquiry_oper(request, oper_type):
    response = Response.ResponseObj()
    user_id = request.GET.get('user_id')
    pub_user_obj = models.Enterprise.objects.get(id=user_id)
    role = int(pub_user_obj.role)

    if request.method == "GET":
        forms_obj = SelectForm(request.GET)
        if forms_obj.is_valid():
            current_page = forms_obj.cleaned_data['current_page']
            length = forms_obj.cleaned_data['length']

            # 总资金记录
            if oper_type == 'total_fund_record':
                # 一级分成钱数
                # one_division_money = models.distribute_money_log.objects.filter(
                #     inviter__enterprise_id=user_id,
                #     status=1
                # ).aggregate(Sum('money')).get('money__sum')
                #
                # # 二级分成钱数
                # two_division_money = models.distribute_money_log.objects.filter(
                #     inviter__enterprise_id=user_id,
                #     status=2
                # ).aggregate(Sum('money')).get('money__sum')

                status = request.GET.get('status')
                """
                status 区分 会员充值 和 提现记录 和 全部数据
                
                all 全部数据
                order 会员充值数据 (订单)
                withdrawal 提现数据
                """

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


                total_amount_renewal = renewal_objs.aggregate(Sum('price')).get('price__sum') # 续费总金额
                total_withdrawal_amount = withdrawal_amount_objs.aggregate(Sum('withdrawal_amount')).get('withdrawal_amount__sum') # 提现总金额

                # 提现 数据
                if status == 'withdrawal':
                    total_amount_funds = total_withdrawal_amount
                    total_number_orders = withdrawal_amount_objs.count()
                    data_list = withdrawal(withdrawal_amount_objs)

                # 订单 数据
                elif status == 'order':
                    total_amount_funds = total_amount_renewal
                    total_number_orders = renewal_objs.count()
                    data_list = purchase_membership(renewal_objs)

                # 全部数据 (订单 提现)
                else:
                    total_amount_funds = total_withdrawal_amount + total_amount_renewal # 资金总额
                    total_number_orders = renewal_objs.count() + withdrawal_amount_objs.count() # 订单总数
                    withdrawal_amount_list = purchase_membership(renewal_objs)
                    renewal_list = withdrawal(withdrawal_amount_objs)
                    renewal_list.extend(withdrawal_amount_list)
                    data_list = sorted(renewal_list, key=lambda x: x['create_date'], reverse=True)

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    data_list = data_list[start_line: stop_line]

                data_dict = {
                    'total_amount_funds': total_amount_funds,
                    'total_number_orders': total_number_orders,
                    'data_list': data_list,
                    'count': len(data_list),
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
                    'count': '数据总数',
                    'total_number_orders': '订单总数',
                    'data_list': [
                        {
                            'consumption_type':'消费类型',
                            'consumer_user': '消费用户',
                            'create_date': '消费时间',
                            'price': '消费金额',
                            'order_number': '订单号',
                        },
                    ],
                }

            # 销售数据
            elif oper_type == 'sales_data':
                objs = models.distribute_money_log.objects.filter(
                    inviter__enterprise_id=user_id
                ).order_by('-create_date')
                total_number_orders = objs.count() # 总订单
                primary_distribution_orders = objs.filter(status=1).count() # 一级订单
                Secondary_distribution_orders = objs.filter(status=2).count() # 二级订单

                data_list = []
                for obj in objs:
                    data_list.append({
                        'distribution_level': obj.get_status_display(),
                        'name': b64decode(obj.user.name),
                        'inviter__name': b64decode(obj.inviter.name),
                        'price': obj.price,
                        'money': obj.money,
                        'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                    })

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    data_list = data_list[start_line: stop_line]

                ret_data = {
                    'total_number_orders': total_number_orders,
                    'primary_distribution_orders': primary_distribution_orders,
                    'Secondary_distribution_orders': Secondary_distribution_orders,
                    'data_list': data_list,
                    'count': len(data_list),
                }

                response.code = 200
                response.msg = '查询成功'
                response.data = ret_data
                response.note = {
                    'total_number_orders': '总订单',
                    'primary_distribution_orders': '一级订单',
                    'Secondary_distribution_orders': '二级订单',
                    'count': '数据总数',
                    'data_list': [
                        {
                            'distribution_level': '分销级别',
                            'name': '充值人名称',
                            'price': '充值金额',
                            'money': '分销金额',
                            'create_date': '创建时间',
                            'inviter__name': '分销人名称',
                        }
                    ],
                }

            # 提现数据
            elif oper_type == 'withdrawal_data':
                objs = models.withdrawal_log.objects.filter(
                    user__enterprise_id=user_id,
                    is_success=1
                ).order_by('-create_date')
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

                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    data_list = data_list[start_line: stop_line]

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'total_amount_withdrawal': total_amount_withdrawal,
                    'data_list': data_list,
                    'count': len(data_list),
                }
                response.note = {
                    'total_amount_withdrawal': '销售总额',
                    'count': '数据总数',
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
            response.code = 301
            response.msg = json.loads(forms_obj.error.as_json())

    else:
        if oper_type == '':
            print('--')

        else:
            response.code = 402
            response.msg = '请求异常'

    return JsonResponse(response.__dict__)




