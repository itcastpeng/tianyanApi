from api import models
from publicFunc import Response
from publicFunc import account, xmldom_parsing
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from publicFunc.weixin.weixin_pay_api import weixin_pay_api
from publicFunc.weixin.weixin_gongzhonghao_api import WeChatApi
from publicFunc.article_oper import get_ent_info
from django.db.models import F, Sum
from api.forms.withdrawal import WithdrawalForm, SelectForm
from publicFunc.base64_encryption import b64decode
import xml.dom.minidom as xmldom, datetime, time, json, os
from api.views_dir.my_celery.celery_url import celery_error_warning


@csrf_exempt
@account.is_token(models.Userprofile)
def weixin_pay(request, oper_type, o_id):
    response = Response.ResponseObj()
    weixin_pay_api_obj = weixin_pay_api()  # 实例 公共函数
    user_id = request.GET.get('user_id')

    if request.method == 'POST':
        # 预支付
        if oper_type == 'yuZhiFu':
            pay_type = request.GET.get('pay_type') # 支付方式 余额支付/微信支付
            try:
                fee_objs = models.renewal_management.objects.filter(id=o_id)
                if fee_objs:
                    models.renewal_log.objects.filter(create_user_id=user_id, isSuccess=0).delete() # 删除未付款的订单

                    userObjs = models.Userprofile.objects.filter(id=user_id)
                    user_obj = userObjs[0]
                    fee_obj = fee_objs[0]

                    price = int(fee_obj.price)                                                  # 支付钱数
                    get_the_length_display = fee_obj.get_the_length_display()                   # 续费时长 (几个月/几年)
                    renewal_number_days = fee_obj.renewal_number_days                           # 续费天数
                    now_date = datetime.datetime.now()
                    overdue_date = (now_date + datetime.timedelta(days=renewal_number_days))  # 续费后 到期时间
                    dingdanhao = weixin_pay_api_obj.shengcheng_dingdanhao()                     # 订单号

                    order_objs = models.renewal_log.objects.filter(pay_order_no=dingdanhao)  # 查询订单日志
                    if not order_objs:

                        # 余额支付
                        if pay_type == 'balance_payment':
                            # 创建订单
                            ren_obj = models.renewal_log.objects.create(
                                pay_order_no=dingdanhao,
                                the_length=get_the_length_display,  # 续费时长
                                renewal_number_days=renewal_number_days,
                                create_user_id=user_id,
                                price=price,
                                original_price=fee_obj.original_price,  # 原价
                                overdue_date=overdue_date,
                            )
                            if float(user_obj.make_money) >= price:
                                userObjs.update(make_money=F('make_money') - price)
                                # 修改到期时间
                                userObjs.update(
                                    overdue_date=overdue_date,
                                    vip_type=2,  # 更改为高级会员
                                )
                                ren_obj.isSuccess = 1
                                response.code = 200
                                response.msg = '支付成功'
                            else:
                                ren_obj.isSuccess = 0
                                response.code = 301
                                response.msg = '余额不足'
                            ren_obj.save()


                        # 微信支付
                        else:
                            data = get_ent_info(user_id)  # 获取用户信息
                            weixin_obj = WeChatApi(data)  # 获取用户公众号信息
                            appid = weixin_obj.APPID  # appid
                            APPSECRET = weixin_obj.APPSECRET  # 商户号
                            data = {
                                'total_fee': price,  # 金额(分 为单位)
                                'openid': user_obj.openid,  # 微信用户唯一标识
                                'appid': appid,  # appid
                                'dingdanhao': dingdanhao  # 生成订单号
                            }

                            # price = price * 100                       # 单位 分
                            result = weixin_pay_api_obj.yuzhifu(data)  # 预支付
                            return_code = result.get('return_code')
                            return_msg = result.get('return_msg')
                            prepay_id = result.get('prepay_id')['prepay_id']

                            if return_code == 'SUCCESS':  # 判断预支付返回参数 是否正确
                                models.renewal_log.objects.create(
                                    pay_order_no=dingdanhao,
                                    the_length=get_the_length_display,  # 续费时长
                                    renewal_number_days=renewal_number_days,
                                    create_user_id=user_id,
                                    price=price,
                                    original_price=fee_obj.original_price,  # 原价
                                    overdue_date=overdue_date,
                                )

                                # 返回数据
                                data_dict = {
                                    'appId': appid,
                                    'timeStamp': int(time.time()),
                                    'nonceStr': weixin_pay_api_obj.generateRandomStamping(),
                                    'package': 'prepay_id=' + prepay_id,
                                    'signType': 'MD5'
                                }
                                SHANGHUKEY = weixin_pay_api_obj.SHANGHUKEY
                                stringSignTemp = weixin_pay_api_obj.shengchengsign(data_dict, SHANGHUKEY)
                                data_dict['paySign'] = weixin_pay_api_obj.md5(stringSignTemp).upper()  # upper转换为大写

                                response.data = data_dict
                                response.code = 200
                                response.msg = '预支付请求成功'
                            else:
                                response.code = 301
                                response.msg = '支付失败, 原因:{}'.format(return_msg)

                else:
                    response.code = 301
                    response.msg = '请选择一项会员'
            except Exception as e:
                if pay_type=='balance_payment':
                    text = '余额支付'
                else:
                    text = '微信支付'

                msg = '警告:{}, \n错误:{}, \n时间:{}'.format(
                    '用户支付报错--->用户ID{}-充值ID{}-充值方式'.format(user_id, o_id, text),
                    e,
                    datetime.datetime.today()
                )
                celery_error_warning(msg)


        # 提现功能
        elif oper_type == 'withdrawal':
            try:
                form_data = {
                    'user_id': user_id,
                    'withdrawal_amount': request.GET.get('withdrawal_amount'), # 提现金额
                }
                form_objs = WithdrawalForm(form_data)
                if form_objs.is_valid():

                    data = get_ent_info(user_id)  # 获取用户信息
                    weixin_obj = WeChatApi(data)  # 获取用户公众号信息
                    appid = weixin_obj.APPID  # appid
                    APPSECRET = weixin_obj.APPSECRET  # 商户号

                    print(request.META)
                    # 当前路径
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    # 获取访问用户IP
                    if request.META.get('HTTP_X_FORWARDED_FOR'):
                        ip = request.META['HTTP_X_FORWARDED_FOR']
                    else:
                        ip = request.META['REMOTE_ADDR']

                    user_obj, withdrawal_amount = form_objs.cleaned_data.get('withdrawal_amount')
                    dingdanhao = weixin_pay_api_obj.shengcheng_dingdanhao()
                    data = {
                        'withdrawal_amount': withdrawal_amount, # 提现金额
                        'dingdanhao': dingdanhao,               # 订单号
                        'appid': appid,                         # appid
                        'openid': user_obj.openid,              # openid
                        'user_id': user_id,                     # user_id
                        'user_name': b64decode(user_obj.name),
                        'make_money': user_obj.make_money,
                        'ip': ip,
                    }
                    response_data = weixin_pay_api_obj.withdrawal(data) # 提现

                    code = response_data.get('code')
                    return_msg = response_data.get('return_msg')

                    make_money = float(user_obj.make_money)             # 用户待提钱数
                    withdrawal_amount = withdrawal_amount    # 用户提现钱数
                    withdrawal_after = make_money - withdrawal_amount   # 待提钱数减去提现钱数

                    if code == 200:
                        is_success = 1 # 是否提现成功
                        response.code = 200
                        # 减去提现的钱数
                        user_money_obj = models.Userprofile.objects.get(id=user_id)
                        user_money_obj.make_money = F('make_money') - withdrawal_amount
                        user_money_obj.save()

                    else:
                        is_success = 0
                        response.code = 301

                    models.withdrawal_log.objects.create(           # 创建提现记录
                        user_id=user_id,
                        withdrawal_befor=make_money,           # 提现前 待提钱数
                        withdrawal_amount=withdrawal_amount,  # 提现金额
                        withdrawal_after=withdrawal_after,  # 提现后 待提钱数
                        is_success=is_success,
                        wechat_returns_data=return_msg,
                        dingdanhao=dingdanhao
                    )

                    response.msg = return_msg
                else:
                    response.code = 301
                    response.msg = json.loads(form_objs.errors.as_json())
            except Exception as e:
                msg = '警告:{}, \n错误:{}, \n时间:{}'.format(
                    '用户提现报错--->用户ID{}, 提现钱数{} '.format(user_id, request.GET.get('withdrawal_amount')),
                    e,
                    datetime.datetime.today()
                )
                celery_error_warning(msg)

    else:

        # 提现记录
        if oper_type == 'withdrawal_record':
            form_objs = SelectForm(request.GET)
            if form_objs.is_valid():
                current_page = form_objs.cleaned_data['current_page']
                length = form_objs.cleaned_data['length']
                user_obj = models.Userprofile.objects.get(id=user_id)

                objs = models.withdrawal_log.objects.filter(user_id=user_id).order_by('-create_date')

                withdrawal_amount_sum_obj = objs.filter(is_success=1).aggregate(
                    nums=Sum('withdrawal_amount')
                )

                data_count = objs.count()
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]
                data_list = []
                for obj in objs:
                    data_list.append({
                        'dingdanhao': obj.dingdanhao,                   # 提现订单号
                        'withdrawal_amount': obj.withdrawal_amount,     # 提现金额
                        'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),     # 提现时间
                        'is_success': obj.is_success,                   # 提现是否成功
                        'wechat_returns_data': obj.wechat_returns_data, # 失败原因
                    })

                withdrawal_amount_sum = 0
                if withdrawal_amount_sum_obj:
                    withdrawal_amount_sum = withdrawal_amount_sum_obj.get('nums')

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'data_count': data_count,
                    'withdrawal_amount_sum': withdrawal_amount_sum,
                    'cumulative_amount': user_obj.cumulative_amount,
                    'make_money': user_obj.make_money,
                    'data_list': data_list,
                }
                response.note = {
                    'withdrawal_amount_sum': '已提现钱数',
                    'cumulative_amount': '累计现金',
                    'make_money': '当前待提余额',
                    'data_list':{
                        'dingdanhao': '提现订单号',
                        'withdrawal_amount': '提现金额',
                        'create_date': '提现时间',
                        'is_success': '提现是否成功',
                        'wechat_returns_data': '失败原因'
                    }

                }
            else:
                response.code = 301
                response.msg = json.loads(form_objs.errors.as_json())

        # 支付记录
        elif oper_type == 'payment_records':
            form_objs = SelectForm(request.GET)
            if form_objs.is_valid():
                current_page = form_objs.cleaned_data['current_page']
                length = form_objs.cleaned_data['length']

                # user_obj = models.Userprofile.objects.get(id=user_id)

                objs = models.renewal_log.objects.filter(
                    create_user_id=user_id,
                    isSuccess=1
                ).order_by('-create_date')

                data_count = objs.count()
                if length != 0:
                    start_line = (current_page - 1) * length
                    stop_line = start_line + length
                    objs = objs[start_line: stop_line]
                data_list = []
                for obj in objs:
                    data_list.append({
                        'pay_order_no': obj.pay_order_no,               # 订单号
                        'price':obj.price,                              # 价钱
                        # 'original_price':obj.original_price,            # 原价
                        'the_length':obj.the_length,                    # 时长
                        # 'overdue_date':obj.overdue_date.strftime('%Y-%m-%d %H:%M:%S'),  # 过期时间
                        'create_date': obj.create_date.strftime('%Y-%m-%d %H:%M:%S'),  # 创建时间
                    })

                response.code = 200
                response.msg = '查询成功'
                response.data = {
                    'data_count': data_count,
                    'data_list': data_list,
                }
                response.note = {
                    'data_list': {
                        'pay_order_no': '订单号',
                        'price': '支付金额',
                        'the_length': '时长',
                        'create_date': '下单时间',
                    }

                }
            else:
                response.code = 301
                response.msg = json.loads(form_objs.errors.as_json())


        else:
            response.code = 402
            response.msg = '请求异常'


    return JsonResponse(response.__dict__)








# 微信回调
def payback(request):
    weixin_pay_api_obj = weixin_pay_api()  # 实例 公共函数
    response = Response.ResponseObj()
    isSuccess = 0
    response.code = 200
    DOMTree = xmldom.parseString(request.body)
    collection = DOMTree.documentElement
    data = ['mch_id', 'return_code', 'appid', 'openid', 'cash_fee', 'out_trade_no']
    resultData = xmldom_parsing.xmldom(collection, data)
    renewal_log_objs = models.renewal_log.objects.filter(pay_order_no=resultData['out_trade_no'])
    if resultData['return_code'] == 'SUCCESS' and renewal_log_objs:   # 如果支付成功 和 有订单
        renewal_log_obj = renewal_log_objs[0]
        if not renewal_log_obj.isSuccess:
            # 查询订单是否付款成功
            result_data = {
                'appid': resultData['appid'],  # appid
                'mch_id': resultData['mch_id'],  # 商户号
                'out_trade_no': resultData['out_trade_no'],  # 订单号
                'nonce_str': weixin_pay_api_obj.generateRandomStamping(),  # 32位随机值
            }
            return_code = weixin_pay_api_obj.weixin_back_pay(result_data)

            if return_code == 'SUCCESS':
                isSuccess = 1 # 支付状态
                pay_user_id = renewal_log_obj.create_user_id  # 充值人  ID
                renewal_log_objs.update(isSuccess=isSuccess)  # 修改充值成功

                # 修改会员到期时间 和高级会员
                user_objs = models.Userprofile.objects.filter(id=pay_user_id)
                user_objs.update(
                    overdue_date=renewal_log_obj.overdue_date,
                    vip_type=2, # 更改为高级会员
                )

                enter_obj = models.Enterprise.objects.get(id=user_objs[0].enterprise_id)
                primary_distribution = float(enter_obj.primary_distribution) / 100       # 一级分销占比
                secondary_distribution = float(enter_obj.secondary_distribution) /100   # 二级分销占比



                inviter_id = None  # 父级 推广人
                if user_objs[0].inviter:
                    inviter_id = user_objs[0].inviter_id

                # 判断是否首次充值 判断是否有邀请人 首次充值给 邀请人增加钱
                renewal_objs = models.renewal_log.objects.filter( # 充值人为自己 且充值成功
                    create_user_id=pay_user_id,
                    isSuccess=1
                )
                if renewal_objs.count() == 1 and inviter_id:  # 判断 是否首次充值 和 是否有 上线人
                    price = float(renewal_objs[0].price) / 100                                              # 首次充值钱数
                    inviter_id_user_obj = models.Userprofile.objects.get(id=inviter_id)
                    if inviter_id_user_obj.vip_type == 2:                                                   # 判断 推广人当前是否为 高级会员
                        cumulative_amount = float(price) * primary_distribution                             # 一级分享人应加钱数  30%  保留小数点后两位
                        inviter_id_user_obj.cumulative_amount = F('cumulative_amount') + cumulative_amount  # 累计钱数 + 30% # 默认
                        inviter_id_user_obj.make_money = F('make_money') + cumulative_amount                # 待提钱数 + 30% # 默认
                        inviter_id_user_obj.save()

                        models.distribute_money_log.objects.create( # 创建充值分销人应得钱数日志
                            user_id=renewal_log_obj.create_user_id,
                            inviter_id=inviter_id,
                            price=price,
                            money=cumulative_amount,
                            status=1,
                            renewal_id=renewal_log_obj.id
                        )

                        if inviter_id_user_obj.inviter:                     # 判断是否有二级分享人
                            two_inviter_id = inviter_id_user_obj.inviter_id # 二级 分享人ID
                            two_user_obj = models.Userprofile.objects.get(id=two_inviter_id)
                            if two_user_obj.vip_type == 2:                                  # 判断 二级分享人 是否为高级会员
                                cumulative_amount = float(price) * secondary_distribution   # 二级分享人应加钱数, 保留小数点后两位
                                two_user_obj.cumulative_amount = F('cumulative_amount') + cumulative_amount
                                two_user_obj.make_money = F('make_money') + cumulative_amount
                                two_user_obj.save()

                                models.distribute_money_log.objects.create( # 创建充值分销人应得钱数日志
                                    user_id=renewal_log_obj.create_user_id,
                                    inviter_id=two_inviter_id,
                                    price=price,
                                    money=cumulative_amount,
                                    status=2,
                                    renewal_id=renewal_log_obj.id
                                )

                print('--------------------支付成功-------------')
            else:
                objs = models.renewal_log.objects.filter(pay_order_no=result_data.get('out_trade_no'))
                if objs:
                    objs.delete()
                print('------支付失败 ----------删除订单')


            renewal_log_objs.update(isSuccess=isSuccess)  # 修改订单状态
    return JsonResponse(response.__dict__)










