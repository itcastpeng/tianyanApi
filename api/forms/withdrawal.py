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
        withdrawal_amount = float(withdrawal_amount)
        if withdrawal_amount <= 200:
            user_obj = models.Userprofile.objects.get(id=user_id)
            if float(user_obj.make_money) >= withdrawal_amount:
                return user_obj, withdrawal_amount

            else:
                self.add_error('withdrawal_amount', '余额不足')
        else:
            self.add_error('withdrawal_amount', '每次最多提现贰佰元人民币')






















