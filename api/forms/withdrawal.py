from django import forms

from api import models
import re





# 提现form验证
class WithdrawalForm(forms.Form):
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            'required': '登录异常'
        }
    )

    withdrawal_amount = forms.CharField(
        required=True,
        error_messages={
            'required': "请填写提现金额"
        }
    )


    def clean_withdrawal_amount(self):
        withdrawal_amount = self.data.get('withdrawal_amount') # 提现金额
        user_id = self.data.get('user_id')
        if withdrawal_amount.isdigit():
            withdrawal_amount = int(withdrawal_amount)
            if withdrawal_amount <= 200:
                user_obj = models.Userprofile.objects.get(id=user_id)
                if float(user_obj.make_money) >= withdrawal_amount:
                    return user_obj, withdrawal_amount

                else:
                    self.add_error('withdrawal_amount', '余额不足')
            else:
                self.add_error('withdrawal_amount', '每次最多提现贰佰元人民币')
        else:
            self.add_error('withdrawal_amount', '不能提现小数')



# 判断是否是数字
class SelectForm(forms.Form):
    current_page = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页码数据类型错误"
        }
    )

    length = forms.IntegerField(
        required=False,
        error_messages={
            'required': "页显示数量类型错误"
        }
    )

    def clean_current_page(self):
        if 'current_page' not in self.data:
            current_page = 1
        else:
            current_page = int(self.data['current_page'])
        return current_page

    def clean_length(self):
        if 'length' not in self.data:
            length = 10
        else:
            length = int(self.data['length'])
        return length


















